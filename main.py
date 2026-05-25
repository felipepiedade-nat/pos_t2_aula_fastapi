import logging
from enum import Enum
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import os
from groq import Groq
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

API_TOKEN = "123"


def common_api_token(api_token: str):
    if api_token != API_TOKEN:
        logger.warning(f"Token inválido recebido: {api_token}")
        raise HTTPException(status_code=401, detail="Token inválido")
    return {"api_token": api_token}


load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI(
    title="APIs da Aula — Felipe Piedade",
    version="0.1",
    summary="API desenvolvida durante a Pós-Graduação em Sistemas e Agentes Inteligentes (UFG-CEIA)",
    description="""
  **API educacional** desenvolvida na disciplina **Construção de APIs para IA**.

  Contém endpoints de:
  - Operações matemáticas em 3 formatos diferentes (path params, query params, Pydantic)
  - Geração de história usando LLM (Groq + Llama 3.1)

  ### Sobre o autor
  Repositório no [GitHub](https://github.com/felipepiedade-nat/pos_t2_aula_fastapi).

  Em caso de dúvidas, entrar em contato pelo e-mail abaixo.
  """,
    contact={
        "name": "Felipe Piedade",
        "url": "https://github.com/felipepiedade-nat",
        "email": "fadpiedade@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    terms_of_service="https://github.com/felipepiedade-nat/pos_t2_aula_fastapi",
    dependencies=[Depends(common_api_token)],
)


class Numeros(BaseModel):
    numero1: int
    numero2: int


class TipoOperacao(str, Enum):
    SOMA = "soma"
    SUBTRACAO = "subtracao"
    MULTIPLICACAO = "multiplicacao"
    DIVISAO = "divisao"


@app.get("/teste")
def hello_world():
    return {"message": "hello world"}


@app.get(
    "/soma/v1/{numero1}/{numero2}",
    tags=["Operações Matemáticas"],
    deprecated=True,
    summary="[DEPRECATED] Use /soma/v3 — será descontinuado em 15/06",
)
def soma_v1(numero1: int, numero2: int):
    return {"resultado": numero1 + numero2}


@app.post("/soma/v2", tags=["Operações Matemáticas"])
def soma_v2(numero1: int, numero2: int):
    return {"resultado": numero1 + numero2}


@app.post("/soma/v3", tags=["Operações Matemáticas"])
def soma_v3(numeros: Numeros):
    logger.info(
        f"Requisição recebida: numero1={numeros.numero1}, numero2={numeros.numero2}"
    )

    if numeros.numero1 < 0 or numeros.numero2 < 0:
        logger.warning("Tentativa de soma com número negativo")
        raise HTTPException(
            status_code=400,
            detail="Os números não podem ser negativos",
        )

    resultado = numeros.numero1 + numeros.numero2
    logger.info(f"Soma calculada com sucesso: {resultado}")
    return {"resultado": resultado}


@app.post("/operacao_matematica", tags=["Operações Matemáticas"])
def operacao_matematica(numeros: Numeros, operacao: TipoOperacao):
    if operacao == TipoOperacao.SOMA:
        resultado = numeros.numero1 + numeros.numero2
    elif operacao == TipoOperacao.SUBTRACAO:
        resultado = numeros.numero1 - numeros.numero2
    elif operacao == TipoOperacao.MULTIPLICACAO:
        resultado = numeros.numero1 * numeros.numero2
    elif operacao == TipoOperacao.DIVISAO:
        if numeros.numero2 == 0:
            raise HTTPException(
                status_code=400, detail="Divisão por zero não permitida"
            )
        resultado = numeros.numero1 / numeros.numero2
    return {"resultado": resultado}


class Historia(BaseModel):
    tema: str


@app.post("/gerar_historia", tags=["IA Generativa"])
def gerar_historia(historia: Historia):
    logger.info(f"Gerando história sobre o tema: {historia.tema}")

    prompt = f"Escreva uma história curta e envolvente sobre o tema: {historia.tema}"

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt},
        ],
        model="llama-3.1-8b-instant",
    )

    historia_gerada = chat_completion.choices[0].message.content
    logger.info("História gerada com sucesso")
    return {"historia": historia_gerada}
