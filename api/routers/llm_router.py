from fastapi import APIRouter

from models import Historia, HistoriaResposta
from utils import execute_prompt, get_logger

logger = get_logger()
router = APIRouter(prefix="/llm", tags=["IA Generativa"])


@router.post(
    "/v1/gerar_historia",
    summary="Gera uma história curta sobre o tema informado",
    response_model=HistoriaResposta,
)
def gerar_historia(historia: Historia) -> HistoriaResposta:
    """Gera uma história a partir do tema usando Groq + Llama 3.1."""
    logger.info(f"Requisição recebida. Tema: {historia.tema}")

    prompt = f"Escreva uma história curta e envolvente sobre o tema: {historia.tema}"
    resultado = execute_prompt(prompt)

    logger.info(f"História gerada com sucesso. Tema: {historia.tema}")
    return HistoriaResposta(historia=resultado)
