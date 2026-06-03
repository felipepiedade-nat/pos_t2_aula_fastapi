import logging
import os

from dotenv import find_dotenv, load_dotenv
from fastapi import HTTPException
from groq import Groq

load_dotenv(find_dotenv())

API_INLINE_TOKEN = os.getenv("API_TOKEN")


def get_logger() -> logging.Logger:
    """Devolve um logger configurado com formato padrão da aplicação.

    Returns:
        logging.Logger: logger pronto para uso em qualquer módulo.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger(__name__)


def verify_api_token(api_token: str) -> dict:
    """Verifica se o token enviado bate com o configurado em ``.env``.

    Args:
        api_token: token recebido como query parameter na requisição.

    Raises:
        HTTPException: status 401 quando o token não confere.

    Returns:
        dict: payload simbólico para reuso futuro via ``Depends``.
    """
    logger = get_logger()
    if api_token != API_INLINE_TOKEN:
        logger.warning(f"Tentativa de acesso com token inválido: {api_token!r}")
        raise HTTPException(status_code=401, detail="Token de autenticação inválido")
    return {"api_token": api_token}


def execute_prompt(prompt: str, model: str = "llama-3.1-8b-instant") -> str:
    """Envia um prompt para a LLM via Groq e devolve o texto gerado.

    Args:
        prompt: instrução completa que será enviada ao modelo.
        model: identificador do modelo Groq. Default leve e rápido.

    Returns:
        str: conteúdo textual da primeira choice retornada pela LLM.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
