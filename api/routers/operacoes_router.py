from fastapi import APIRouter, HTTPException, status

from models import Numeros, Resultado, TipoOperacao
from utils import RESPOSTAS_PROTEGIDAS, get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/operacoes", tags=["Operações Matemáticas"])


@router.get(
    "/soma/v1/{numero1}/{numero2}",
    deprecated=True,
    summary="[DEPRECATED] Soma via path params — será descontinuado em 15/06",
    response_model=Resultado,
    responses={
        200: {"description": "Soma calculada com sucesso"},
        **RESPOSTAS_PROTEGIDAS,
    },
)
def soma_v1(numero1: int, numero2: int) -> Resultado:
    """Soma dois números recebidos pela URL (formato legado)."""
    return Resultado(resultado=numero1 + numero2)


@router.post(
    "/soma/v2",
    summary="Soma via query params",
    response_model=Resultado,
    responses={
        200: {"description": "Soma calculada com sucesso"},
        **RESPOSTAS_PROTEGIDAS,
    },
)
def soma_v2(numero1: int, numero2: int) -> Resultado:
    """Soma dois números recebidos como query parameters."""
    return Resultado(resultado=numero1 + numero2)


@router.post(
    "/soma/v3",
    summary="Soma via BaseModel (formato recomendado para produção)",
    description="Recebe dois números no corpo da requisição e devolve a soma.",
    response_description="Soma calculada com sucesso",
    status_code=status.HTTP_201_CREATED,
    response_model=Resultado,
    responses={
        201: {"description": "Soma calculada com sucesso"},
        400: {"description": "Números negativos não são aceitos"},
        **RESPOSTAS_PROTEGIDAS,
    },
)
def soma_v3(numeros: Numeros) -> Resultado:
    """Soma dois números enviados como JSON, validando que sejam não-negativos."""
    logger.info(
        f"Soma v3 recebida: numero1={numeros.numero1}, numero2={numeros.numero2}"
    )
    if numeros.numero1 < 0 or numeros.numero2 < 0:
        logger.warning("Tentativa de soma com número negativo")
        raise HTTPException(
            status_code=400, detail="Os números não podem ser negativos"
        )
    return Resultado(resultado=numeros.numero1 + numeros.numero2)


@router.post(
    "/operacao_matematica",
    summary="Operação matemática genérica (soma, subtração, multiplicação, divisão)",
    response_model=Resultado,
    responses={
        200: {"description": "Operação realizada com sucesso"},
        400: {"description": "Divisão por zero não permitida"},
        **RESPOSTAS_PROTEGIDAS,
    },
)
def operacao_matematica(numeros: Numeros, operacao: TipoOperacao) -> Resultado:
    """Aplica a operação selecionada via Enum sobre dois números."""
    a, b = numeros.numero1, numeros.numero2
    if operacao == TipoOperacao.SOMA:
        return Resultado(resultado=a + b)
    if operacao == TipoOperacao.SUBTRACAO:
        return Resultado(resultado=a - b)
    if operacao == TipoOperacao.MULTIPLICACAO:
        return Resultado(resultado=a * b)
    if operacao == TipoOperacao.DIVISAO:
        if b == 0:
            logger.warning("Tentativa de divisão por zero bloqueada")
            raise HTTPException(
                status_code=400, detail="Divisão por zero não permitida"
            )
        return Resultado(resultado=a / b)
