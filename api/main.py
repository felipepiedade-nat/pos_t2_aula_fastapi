from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from routers.auth_router import router as auth_router
from routers.juridico_router import router_v1 as juridico_router_v1
from routers.juridico_router import router_v2 as juridico_router_v2
from routers.llm_router import router as llm_router
from routers.operacoes_router import router as operacoes_router
from utils import configurar_logs, get_logger, verify_jwt_token

configurar_logs()
logger = get_logger(__name__)

app = FastAPI(
    title="APIs da Aula — Felipe Piedade",
    version="0.3",
    summary="API desenvolvida durante a Pós-Graduação em Sistemas e Agentes Inteligentes (UFG-CEIA)",
    description="""
**API educacional** desenvolvida na disciplina **Construção de APIs para IA**.

### Endpoints de IA avaliados no trabalho final

**v1 — texto colado (JSON):**

- `POST /api/v1/juridico/classificar_peticao` — classifica em 1 das 15 áreas do Direito
- `POST /api/v1/juridico/extrair_pedidos` — lista objetiva dos pedidos

**v2 — upload de arquivo PDF/DOCX (multipart/form-data):**

- `POST /api/v2/juridico/classificar_peticao` — mesma classificação, mas a partir do arquivo
- `POST /api/v2/juridico/extrair_pedidos` — mesma extração, mas a partir do arquivo

Limites do v2: 5 MB, 50 páginas, 50–20.000 caracteres extraídos.

### Endpoints de apoio (Aula 2)

- Operações matemáticas em 3 formatos (path params, query params, Pydantic)
- Operação matemática genérica via `Enum`
- `gerar_historia` mantido como `deprecated` para fins didáticos

### Autenticação

1. Faça login em **`POST /api/v1/auth/token`** com `usuario` e `senha`.
2. Copie o `access_token` retornado.
3. Clique em **Authorize** no Swagger e cole o token.
4. Todos os endpoints sob `/api/v1/` (exceto `/auth/token`) passam a aceitar
   o header `Authorization: Bearer <JWT>` automaticamente.

O JWT expira em 1h (configurável em `JWT_EXPIRA_SEGUNDOS`).

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
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Padroniza a resposta de qualquer ``HTTPException`` lançada na app."""
    logger.warning(
        f"HTTPException {exc.status_code} em {request.method} {request.url.path}: {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"erro": exc.detail, "status_code": exc.status_code},
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Converte erros de validação Pydantic em 422 estruturado."""
    logger.warning(
        f"Validação falhou em {request.method} {request.url.path}: {exc.errors()}"
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "erro": "Dados de entrada inválidos",
            "detalhes": exc.errors(),
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Captura qualquer erro não previsto, loga com stacktrace e devolve 500."""
    logger.exception(f"Erro nao tratado em {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "erro": "Erro interno do servidor",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
    )


@app.get("/", tags=["Saúde"])
def root() -> dict:
    """Endpoint público que confirma que a API está no ar."""
    return {"status": "ok", "docs": "/docs"}


@app.get("/teste", tags=["Saúde"])
def hello_world() -> dict:
    """Endpoint de teste rápido, sem autenticação."""
    return {"message": "hello world"}


app.include_router(auth_router, prefix="/api/v1")
app.include_router(
    juridico_router_v1,
    prefix="/api/v1",
    dependencies=[Depends(verify_jwt_token)],
)
app.include_router(
    juridico_router_v2,
    prefix="/api/v2",
    dependencies=[Depends(verify_jwt_token)],
)
app.include_router(
    operacoes_router,
    prefix="/api/v1",
    dependencies=[Depends(verify_jwt_token)],
)
app.include_router(
    llm_router,
    prefix="/api/v1",
    dependencies=[Depends(verify_jwt_token)],
)
