from fastapi import APIRouter, HTTPException, status

from models import (
    AreaJuridica,
    ClassificacaoOutput,
    PedidosOutput,
    PeticaoInput,
)
from utils import execute_prompt_json, get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/juridico", tags=["Jurídico"])


AREAS_VALIDAS = ", ".join(a.value for a in AreaJuridica)


@router.post(
    "/classificar_peticao",
    summary="Classifica uma petição por área do Direito",
    description=(
        "Recebe o texto de uma petição inicial (ou trecho dela) e usa uma LLM "
        "para identificar a área do Direito predominante. Devolve o rótulo da "
        "área (valor fechado do Enum AreaJuridica) e uma justificativa em "
        "linguagem natural com os termos que motivaram a classificação."
    ),
    response_model=ClassificacaoOutput,
    status_code=status.HTTP_200_OK,
)
def classificar_peticao(peticao: PeticaoInput) -> ClassificacaoOutput:
    """Classifica a petição usando a LLM e valida a área retornada."""
    logger.info(f"Classificando petição ({len(peticao.texto)} caracteres)")

    prompt = (
        "Você é um assistente especialista em Direito brasileiro. "
        "Sua tarefa é classificar a petição abaixo em uma das áreas do "
        "Direito listadas a seguir.\n\n"
        f"Áreas válidas (use exatamente um destes valores): {AREAS_VALIDAS}\n\n"
        "Se o texto não se encaixar bem em nenhuma das 14 primeiras, "
        'use "outra". Não invente novas áreas.\n\n'
        "Responda APENAS com um objeto JSON com este formato exato:\n"
        '{"area": "<uma das áreas válidas>", "justificativa": "<2 a 4 frases citando termos do texto>"}\n\n'
        f"Texto da petição:\n---\n{peticao.texto}\n---"
    )

    resposta = execute_prompt_json(prompt)

    area_bruta = resposta.get("area", "").strip().lower()
    justificativa = resposta.get("justificativa", "").strip()

    try:
        area = AreaJuridica(area_bruta)
    except ValueError:
        logger.warning(
            f"LLM devolveu area fora do Enum: {area_bruta!r}. Usando 'outra'."
        )
        area = AreaJuridica.OUTRA

    if not justificativa:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM não devolveu justificativa para a classificação",
        )

    logger.info(f"Petição classificada como: {area.value}")
    return ClassificacaoOutput(area=area, justificativa=justificativa)


@router.post(
    "/extrair_pedidos",
    summary="Extrai a lista de pedidos de uma petição",
    description=(
        "Recebe o texto de uma petição inicial e devolve a lista objetiva "
        "dos pedidos formulados pelo autor ao juiz. Cada pedido vira um item "
        "da lista, em linguagem direta e sem ritual cartorário."
    ),
    response_model=PedidosOutput,
    status_code=status.HTTP_200_OK,
)
def extrair_pedidos(peticao: PeticaoInput) -> PedidosOutput:
    """Extrai os pedidos da petição usando a LLM."""
    logger.info(f"Extraindo pedidos de petição ({len(peticao.texto)} caracteres)")

    prompt = (
        "Você é um assistente especialista em Direito brasileiro. "
        "Sua tarefa é extrair a lista de pedidos que o autor faz ao juiz "
        "no texto da petição abaixo.\n\n"
        "Regras:\n"
        "- Cada pedido vira um item da lista.\n"
        "- Escreva cada pedido em uma frase objetiva, sem ritual cartorário "
        '("requer-se", "Vossa Excelência", etc.).\n'
        "- Inclua valores quando o pedido mencionar (R$ X, prazo Y).\n"
        "- Se não houver pedido identificável, devolva lista vazia.\n\n"
        "Responda APENAS com um objeto JSON com este formato exato:\n"
        '{"pedidos": ["pedido 1", "pedido 2", ...]}\n\n'
        f"Texto da petição:\n---\n{peticao.texto}\n---"
    )

    resposta = execute_prompt_json(prompt)

    pedidos_bruto = resposta.get("pedidos", [])
    if not isinstance(pedidos_bruto, list):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM não devolveu uma lista de pedidos",
        )

    pedidos = [str(p).strip() for p in pedidos_bruto if str(p).strip()]

    logger.info(f"Pedidos extraídos: {len(pedidos)}")
    return PedidosOutput(quantidade_pedidos=len(pedidos), pedidos=pedidos)
