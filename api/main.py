from fastapi import Depends, FastAPI

from routers.llm_router import router as llm_router
from routers.operacoes_router import router as operacoes_router
from utils import get_logger, verify_api_token

logger = get_logger()

app = FastAPI(
    title="APIs da Aula — Felipe Piedade",
    version="0.2",
    summary="API desenvolvida durante a Pós-Graduação em Sistemas e Agentes Inteligentes (UFG-CEIA)",
    description="""
**API educacional** desenvolvida na disciplina **Construção de APIs para IA**.

Endpoints disponíveis:

- Operações matemáticas em 3 formatos (path params, query params, Pydantic)
- Operação matemática genérica via `Enum`
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
    dependencies=[Depends(verify_api_token)],
)


@app.get("/teste", tags=["Saúde"])
def hello_world() -> dict:
    """Endpoint de teste rápido para confirmar que a API está no ar."""
    return {"message": "hello world"}


app.include_router(operacoes_router)
app.include_router(llm_router)
