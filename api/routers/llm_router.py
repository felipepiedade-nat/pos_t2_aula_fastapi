from fastapi import APIRouter

from models import Historia, HistoriaResposta
from utils import execute_prompt, get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/llm", tags=["IA Generativa"])


@router.post(
    "/gerar_historia",
    summary="[DEPRECATED — Aula 2] Gera uma história curta sobre o tema informado",
    description=(
        "Endpoint mantido como demonstração da Aula 2. Os endpoints "
        "avaliados no trabalho final são os de `/juridico/`."
    ),
    response_model=HistoriaResposta,
    deprecated=True,
)
def gerar_historia(historia: Historia) -> HistoriaResposta:
    """Gera uma história a partir do tema usando Groq + Llama 3.1."""
    logger.info(f"Requisição recebida. Tema: {historia.tema}")

    prompt = f"Escreva uma história curta e envolvente sobre o tema: {historia.tema}"
    resultado = execute_prompt(prompt)

    logger.info(f"História gerada com sucesso. Tema: {historia.tema}")
    return HistoriaResposta(historia=resultado)
