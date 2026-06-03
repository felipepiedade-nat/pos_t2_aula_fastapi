from fastapi import APIRouter, HTTPException, status

from models import LoginInput, TokenResposta
from utils import autenticar_usuario, criar_jwt, get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/token",
    summary="Gera um JWT a partir de usuário e senha",
    description=(
        "Recebe credenciais (usuário + senha) e devolve um JWT com expiração. "
        "Use o `access_token` retornado no botão **Authorize** do Swagger ou "
        "no header `Authorization: Bearer <token>` das demais rotas."
    ),
    response_model=TokenResposta,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Login bem-sucedido — JWT emitido"},
        401: {"description": "Usuário ou senha inválidos"},
        422: {"description": "Payload inválido (campos faltando ou tipo errado)"},
    },
)
def login(credenciais: LoginInput) -> TokenResposta:
    """Valida usuário/senha e devolve um JWT com expiração."""
    logger.info(f"Tentativa de login do usuário: {credenciais.usuario}")

    if not autenticar_usuario(credenciais.usuario, credenciais.senha):
        logger.warning(f"Falha de login para usuário: {credenciais.usuario}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token, expira_em = criar_jwt(credenciais.usuario)
    logger.info(f"JWT emitido para usuário: {credenciais.usuario}")
    return TokenResposta(access_token=token, expira_em=expira_em)
