from enum import Enum

from pydantic import BaseModel, Field


class Numeros(BaseModel):
    numero1: int = Field(..., description="Primeiro número da operação", examples=[5])
    numero2: int = Field(..., description="Segundo número da operação", examples=[3])


class Resultado(BaseModel):
    resultado: float = Field(..., description="Resultado da operação matemática")


class TipoOperacao(str, Enum):
    SOMA = "soma"
    SUBTRACAO = "subtracao"
    MULTIPLICACAO = "multiplicacao"
    DIVISAO = "divisao"


class Historia(BaseModel):
    tema: str = Field(
        ...,
        description="Tema central da história a ser gerada pela LLM",
        examples=["Natal"],
    )


class HistoriaResposta(BaseModel):
    historia: str = Field(..., description="Texto gerado pela LLM")
