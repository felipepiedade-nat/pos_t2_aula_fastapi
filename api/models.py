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


class AreaJuridica(str, Enum):
    """Áreas do Direito brasileiro suportadas pelo classificador."""

    CIVEL = "civel"
    TRABALHISTA = "trabalhista"
    PENAL = "penal"
    TRIBUTARIA = "tributaria"
    ADMINISTRATIVA = "administrativa"
    CONSTITUCIONAL = "constitucional"
    PREVIDENCIARIA = "previdenciaria"
    EMPRESARIAL = "empresarial"
    CONSUMIDOR = "consumidor"
    AMBIENTAL = "ambiental"
    ELEITORAL = "eleitoral"
    MILITAR = "militar"
    INTERNACIONAL = "internacional"
    DIGITAL = "digital"
    OUTRA = "outra"


class PeticaoInput(BaseModel):
    """Texto de uma petição inicial ou trecho relevante dela."""

    texto: str = Field(
        ...,
        min_length=50,
        max_length=20_000,
        description="Conteúdo textual da petição a ser analisada (50-20000 caracteres)",
        examples=[
            "Excelentíssimo Senhor Doutor Juiz de Direito da Vara do Trabalho. "
            "O reclamante foi demitido sem justa causa em 10/03/2025 após 3 anos "
            "de serviço, sem recebimento das verbas rescisórias devidas..."
        ],
    )


class ClassificacaoOutput(BaseModel):
    """Resultado da classificação de uma petição por área do Direito."""

    area: AreaJuridica = Field(..., description="Área do Direito identificada pela LLM")
    justificativa: str = Field(
        ...,
        description="Termos e elementos do texto que motivaram a classificação",
    )


class PedidosOutput(BaseModel):
    """Lista dos pedidos extraídos da petição."""

    quantidade_pedidos: int = Field(
        ..., ge=0, description="Número total de pedidos identificados"
    )
    pedidos: list[str] = Field(
        ...,
        description="Cada item é um pedido em linguagem objetiva",
    )
