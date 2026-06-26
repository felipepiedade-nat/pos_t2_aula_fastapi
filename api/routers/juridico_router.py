from fastapi import APIRouter, File, HTTPException, UploadFile, status

from models import (
    AreaJuridica,
    ClassificacaoOutput,
    PedidosOutput,
    PeticaoInput,
    TriagemTrabalhistaOutput,
)
from utils import (
    RESPOSTAS_PROTEGIDAS,
    execute_prompt_json,
    extrair_texto_arquivo,
    get_logger,
)

logger = get_logger(__name__)

router_v1 = APIRouter(prefix="/juridico", tags=["Jurídico v1 (texto)"])
router_v2 = APIRouter(prefix="/juridico", tags=["Jurídico v2 (arquivo)"])


AREAS_VALIDAS = ", ".join(a.value for a in AreaJuridica)


def _classificar(texto: str) -> ClassificacaoOutput:
    """Classifica o texto da petição via LLM e devolve o resultado tipado."""
    prompt = (
        "Você é um assistente especialista em Direito brasileiro. "
        "Sua tarefa é classificar a petição abaixo em uma das áreas do "
        "Direito listadas a seguir.\n\n"
        f"Áreas válidas (use exatamente um destes valores): {AREAS_VALIDAS}\n\n"
        "Se o texto não se encaixar bem em nenhuma das 14 primeiras, "
        'use "outra". Não invente novas áreas.\n\n'
        "Responda APENAS com um objeto JSON com este formato exato:\n"
        '{"area": "<uma das áreas válidas>", "justificativa": "<2 a 4 frases citando termos do texto>"}\n\n'
        f"Texto da petição:\n---\n{texto}\n---"
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


def _extrair_pedidos(texto: str) -> PedidosOutput:
    """Extrai os pedidos do texto da petição via LLM."""
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
        f"Texto da petição:\n---\n{texto}\n---"
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


def _lista_de_strings(valor) -> list[str]:
    """Normaliza um campo da resposta da LLM para list[str] limpa."""
    if not isinstance(valor, list):
        return []
    return [str(item).strip() for item in valor if str(item).strip()]


def _triagem_trabalhista(texto: str) -> TriagemTrabalhistaOutput:
    """Faz a triagem de uma petição trabalhista via LLM.

    Separa o conteúdo em temas da fundamentação, direitos materiais
    pleiteados e requerimentos processuais/preliminares.
    """
    prompt = (
        "Você é um assistente especializado em Processo do Trabalho brasileiro. "
        "Sua tarefa é ler a petição inicial abaixo e fazer a triagem do seu "
        "conteúdo com precisão.\n\n"
        "Extraia estritamente:\n"
        "1. temas: os títulos dos temas tratados na fundamentação "
        "(ex: 'Do Contrato de Trabalho', 'Da Rescisão Indireta').\n"
        "2. direitos_trabalhistas: os direitos materiais/pedidos principais "
        "(ex: 'Adicional de insalubridade 40%', 'Saldo de salário').\n"
        "3. requerimentos_preliminares: os requerimentos processuais, "
        "preliminares ou de rito (ex: 'Juízo 100% Digital', 'Justiça Gratuita').\n\n"
        "Não inclua dados contratuais gerais nem pontos de controvérsia. "
        "Se algum eixo não tiver itens, devolva lista vazia.\n\n"
        "Responda APENAS com um objeto JSON com este formato exato:\n"
        '{"temas": [...], "direitos_trabalhistas": [...], '
        '"requerimentos_preliminares": [...]}\n\n'
        f"Texto da petição:\n---\n{texto}\n---"
    )

    resposta = execute_prompt_json(prompt)
    triagem = TriagemTrabalhistaOutput(
        temas=_lista_de_strings(resposta.get("temas")),
        direitos_trabalhistas=_lista_de_strings(resposta.get("direitos_trabalhistas")),
        requerimentos_preliminares=_lista_de_strings(
            resposta.get("requerimentos_preliminares")
        ),
    )
    logger.info(
        "Triagem trabalhista: "
        f"{len(triagem.temas)} temas, "
        f"{len(triagem.direitos_trabalhistas)} direitos, "
        f"{len(triagem.requerimentos_preliminares)} requerimentos"
    )
    return triagem


@router_v1.post(
    "/classificar_peticao",
    summary="Classifica uma petição por área do Direito (texto colado)",
    description=(
        "Recebe o texto de uma petição inicial em JSON e devolve a área do "
        "Direito predominante (Enum AreaJuridica) + justificativa."
    ),
    response_model=ClassificacaoOutput,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Classificação realizada com sucesso"},
        **RESPOSTAS_PROTEGIDAS,
    },
)
def classificar_peticao_texto(peticao: PeticaoInput) -> ClassificacaoOutput:
    """Endpoint v1: recebe texto colado, classifica."""
    logger.info(f"v1 classificar_peticao - {len(peticao.texto)} chars")
    return _classificar(peticao.texto)


@router_v1.post(
    "/extrair_pedidos",
    summary="Extrai a lista de pedidos de uma petição (texto colado)",
    description=(
        "Recebe o texto de uma petição inicial em JSON e devolve a lista "
        "objetiva dos pedidos formulados ao juiz."
    ),
    response_model=PedidosOutput,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Pedidos extraídos com sucesso"},
        **RESPOSTAS_PROTEGIDAS,
    },
)
def extrair_pedidos_texto(peticao: PeticaoInput) -> PedidosOutput:
    """Endpoint v1: recebe texto colado, extrai pedidos."""
    logger.info(f"v1 extrair_pedidos - {len(peticao.texto)} chars")
    return _extrair_pedidos(peticao.texto)


@router_v2.post(
    "/classificar_peticao",
    summary="Classifica uma petição por área do Direito (upload PDF ou DOCX)",
    description=(
        "Recebe o arquivo da petição (.pdf ou .docx) via multipart/form-data, "
        "extrai o texto e classifica em uma das 15 áreas do Direito.\n\n"
        "Limites: 5 MB por arquivo, 50 páginas (PDF), entre 50 e 12.000 caracteres "
        "extraídos. PDFs escaneados (imagem, sem texto extraível) são rejeitados com 422."
    ),
    response_model=ClassificacaoOutput,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Classificação realizada com sucesso"},
        413: {"description": "Arquivo excede 5 MB"},
        **RESPOSTAS_PROTEGIDAS,
    },
)
async def classificar_peticao_arquivo(
    arquivo: UploadFile = File(..., description="Petição em .pdf ou .docx"),
) -> ClassificacaoOutput:
    """Endpoint v2: recebe upload do arquivo, extrai texto, classifica."""
    logger.info(f"v2 classificar_peticao - arquivo: {arquivo.filename}")
    texto = await extrair_texto_arquivo(arquivo)
    return _classificar(texto)


@router_v2.post(
    "/extrair_pedidos",
    summary="Extrai a lista de pedidos de uma petição (upload PDF ou DOCX)",
    description=(
        "Recebe o arquivo da petição (.pdf ou .docx) via multipart/form-data, "
        "extrai o texto e devolve a lista objetiva dos pedidos formulados.\n\n"
        "Limites: 5 MB por arquivo, 50 páginas (PDF), entre 50 e 12.000 caracteres extraídos."
    ),
    response_model=PedidosOutput,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Pedidos extraídos com sucesso"},
        413: {"description": "Arquivo excede 5 MB"},
        **RESPOSTAS_PROTEGIDAS,
    },
)
async def extrair_pedidos_arquivo(
    arquivo: UploadFile = File(..., description="Petição em .pdf ou .docx"),
) -> PedidosOutput:
    """Endpoint v2: recebe upload do arquivo, extrai texto, extrai pedidos."""
    logger.info(f"v2 extrair_pedidos - arquivo: {arquivo.filename}")
    texto = await extrair_texto_arquivo(arquivo)
    return _extrair_pedidos(texto)


@router_v1.post(
    "/triagem_peticao",
    summary="Triagem trabalhista de uma petição (texto colado)",
    description=(
        "Recebe o texto de uma petição inicial trabalhista em JSON e devolve "
        "a triagem em três eixos: temas da fundamentação, direitos materiais "
        "pleiteados e requerimentos preliminares/processuais.\n\n"
        "Endpoint contribuído por Edison (colega de turma)."
    ),
    response_model=TriagemTrabalhistaOutput,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Triagem realizada com sucesso"},
        **RESPOSTAS_PROTEGIDAS,
    },
)
def triagem_peticao_texto(peticao: PeticaoInput) -> TriagemTrabalhistaOutput:
    """Endpoint v1: recebe texto colado, faz a triagem trabalhista."""
    logger.info(f"v1 triagem_peticao - {len(peticao.texto)} chars")
    return _triagem_trabalhista(peticao.texto)


@router_v2.post(
    "/triagem_peticao",
    summary="Triagem trabalhista de uma petição (upload PDF ou DOCX)",
    description=(
        "Recebe o arquivo da petição (.pdf ou .docx) via multipart/form-data, "
        "extrai o texto e devolve a triagem em três eixos: temas da "
        "fundamentação, direitos materiais pleiteados e requerimentos "
        "preliminares/processuais.\n\n"
        "Limites: 5 MB por arquivo, 50 páginas (PDF), entre 50 e 12.000 "
        "caracteres extraídos.\n\n"
        "Endpoint contribuído por Edison (colega de turma)."
    ),
    response_model=TriagemTrabalhistaOutput,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Triagem realizada com sucesso"},
        413: {"description": "Arquivo excede 5 MB"},
        **RESPOSTAS_PROTEGIDAS,
    },
)
async def triagem_peticao_arquivo(
    arquivo: UploadFile = File(..., description="Petição em .pdf ou .docx"),
) -> TriagemTrabalhistaOutput:
    """Endpoint v2: recebe upload do arquivo, extrai texto, faz a triagem."""
    logger.info(f"v2 triagem_peticao - arquivo: {arquivo.filename}")
    texto = await extrair_texto_arquivo(arquivo)
    return _triagem_trabalhista(texto)
