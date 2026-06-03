import logging
import logging.config
import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from groq import Groq

load_dotenv(find_dotenv())

API_INLINE_TOKEN = os.getenv("API_TOKEN")

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "padrao": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "padrao",
        },
        "arquivo_app": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "padrao",
            "filename": str(LOGS_DIR / "app.log"),
            "maxBytes": 1_000_000,
            "backupCount": 5,
            "encoding": "utf-8",
        },
        "arquivo_erros": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "padrao",
            "filename": str(LOGS_DIR / "erros.log"),
            "maxBytes": 1_000_000,
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "arquivo_app", "arquivo_erros"],
    },
}


def configurar_logs() -> None:
    """Aplica a configuração de logging definida em LOGGING_CONFIG."""
    logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(nome: str = __name__) -> logging.Logger:
    """Devolve um logger nomeado já configurado.

    Args:
        nome: nome do logger (geralmente ``__name__`` do módulo chamador).

    Returns:
        logging.Logger: logger pronto para uso.
    """
    return logging.getLogger(nome)


security_scheme = HTTPBearer(
    scheme_name="BearerAuth",
    description="Autenticação via header Authorization: Bearer <token>",
)


def verify_api_token(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    """Verifica se o Bearer Token enviado bate com ``API_TOKEN`` do ``.env``.

    Args:
        credentials: credenciais extraídas do header ``Authorization`` pelo
            FastAPI via ``HTTPBearer``.

    Raises:
        HTTPException: status 401 quando o token está ausente ou inválido.

    Returns:
        dict: payload simbólico para reuso futuro via ``Depends``.
    """
    logger = get_logger(__name__)
    if credentials is None or credentials.credentials != API_INLINE_TOKEN:
        token_recebido = credentials.credentials if credentials else None
        logger.warning(f"Tentativa de acesso com token inválido: {token_recebido!r}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação inválido ou ausente",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"token": credentials.credentials}


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
