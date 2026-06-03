import json
import logging
import logging.config
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from dotenv import find_dotenv, load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from groq import Groq

load_dotenv(find_dotenv())

JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALGORITHM = "HS256"
JWT_EXPIRA_SEGUNDOS = int(os.getenv("JWT_EXPIRA_SEGUNDOS", "3600"))

USUARIOS = {
    "felipe": "123456",
    "rogerio": "123456",
}

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


def autenticar_usuario(usuario: str, senha: str) -> bool:
    """Confere se o par usuário/senha existe em ``USUARIOS``.

    Args:
        usuario: nome de usuário enviado no login.
        senha: senha enviada no login.

    Returns:
        bool: True se as credenciais batem, False caso contrário.
    """
    return USUARIOS.get(usuario) == senha


def criar_jwt(usuario: str) -> tuple[str, int]:
    """Gera um JWT assinado para o usuário, com expiração em segundos.

    Args:
        usuario: nome de usuário a ser embutido no claim ``sub``.

    Returns:
        tuple: (token_jwt, expira_em_segundos).
    """
    agora = datetime.now(tz=timezone.utc)
    expira = agora + timedelta(seconds=JWT_EXPIRA_SEGUNDOS)
    payload = {
        "sub": usuario,
        "iat": int(agora.timestamp()),
        "exp": int(expira.timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, JWT_EXPIRA_SEGUNDOS


security_scheme = HTTPBearer(
    scheme_name="BearerAuth",
    description="Autenticação via header Authorization: Bearer <JWT>",
)


RESPOSTAS_PROTEGIDAS = {
    401: {"description": "Token Bearer ausente, inválido ou expirado"},
    422: {"description": "Payload inválido (validação Pydantic)"},
    500: {"description": "Erro interno do servidor — ver logs/erros.log"},
}


def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    """Valida o JWT enviado no header ``Authorization: Bearer <token>``.

    Args:
        credentials: credenciais extraídas pelo ``HTTPBearer``.

    Raises:
        HTTPException 401: token ausente, inválido ou expirado.

    Returns:
        dict: payload do JWT (inclui ``sub`` com o nome do usuário).
    """
    logger = get_logger(__name__)
    if credentials is None:
        logger.warning("Tentativa de acesso sem header Authorization")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Bearer ausente",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        logger.warning("Tentativa de acesso com token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado — faça login novamente",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as exc:
        logger.warning(f"Tentativa de acesso com token inválido: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


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


def execute_prompt_json(prompt: str, model: str = "llama-3.1-8b-instant") -> dict:
    """Pede à LLM uma resposta em JSON estruturado e devolve já parseado.

    Usa ``response_format={"type": "json_object"}`` da Groq, que força o
    modelo a emitir JSON sintaticamente válido. Em caso de erro de parse
    (raro mas possível), levanta ``HTTPException`` 500.

    Args:
        prompt: instrução; deve indicar explicitamente o schema esperado.
        model: identificador do modelo Groq.

    Returns:
        dict: payload JSON já parseado em estrutura Python.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    conteudo = response.choices[0].message.content
    try:
        return json.loads(conteudo)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM devolveu JSON inválido: {exc}",
        )
