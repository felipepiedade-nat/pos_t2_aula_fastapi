# APIs da Aula — Pós-Graduação UFG-CEIA

API educacional desenvolvida na disciplina **Construção de APIs para IA** da Pós-Graduação em Sistemas e Agentes Inteligentes (UFG-CEIA).

**Autor:** Felipe Piedade

## O que essa API faz

- **Operações matemáticas** em 3 formatos diferentes (path params, query params, Pydantic `BaseModel`)
- **Operação matemática genérica** com `Enum` (soma, subtração, multiplicação, divisão)
- **Geração de histórias** usando LLM (Groq + Llama 3.1)
- **Autenticação global** via token simples (`?api_token=...`)
- **Validação automática** com Pydantic + `HTTPException` customizadas
- **Logging estruturado** com níveis INFO/WARNING
- **Estrutura modular** em routers separados (`api/routers/`)

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) instalado
- Chave de API do Groq (gratuita em <https://console.groq.com/>)

## Configuração

1. Clone o repositório:

   ```bash
   git clone https://github.com/felipepiedade-nat/pos_t2_aula_fastapi.git
   cd pos_t2_aula_fastapi
   ```

2. Instale as dependências:

   ```bash
   uv sync
   ```

3. Crie um arquivo `.env` na raiz a partir do `.env.sample` e preencha:

   ```env
   GROQ_API_KEY=gsk_sua_chave_aqui
   API_TOKEN=defina_um_token_qualquer
   ```

## Executar localmente

```bash
uv run fastapi dev api/main.py
```

A aplicação fica disponível em:

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs?api_token=SEU_TOKEN>
- Redoc: <http://localhost:8000/redoc?api_token=SEU_TOKEN>

> ⚠️ Todos os endpoints exigem o query parameter `?api_token=...` (token didático definido no `.env`).

## Endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/teste` | Hello World |
| GET | `/operacoes/soma/v1/{n1}/{n2}` | Soma via path params (deprecated) |
| POST | `/operacoes/soma/v2` | Soma via query params |
| POST | `/operacoes/soma/v3` | Soma via Pydantic BaseModel |
| POST | `/operacoes/operacao_matematica` | Operação genérica (soma/sub/mult/div) |
| POST | `/llm/v1/gerar_historia` | Gera história usando LLM (Groq) |

## Stack

- **FastAPI** — framework web
- **Pydantic** — validação de dados
- **uv** — gerenciador de pacotes
- **Groq + Llama 3.1** — LLM para geração de texto
- **python-dotenv** — variáveis de ambiente
- **Ruff** — linter e formatter

## Estrutura do projeto

```
pos_t2_aula_fastapi/
├── api/
│   ├── main.py             # instancia FastAPI + include_router
│   ├── models.py           # BaseModels (Pydantic) e Enums
│   ├── utils.py            # logger, autenticação, gateway da LLM
│   ├── docs/
│   │   └── padroes_de_desenvolvimento.md
│   └── routers/
│       ├── llm_router.py
│       └── operacoes_router.py
├── .env                    # segredos reais (NÃO versionado)
├── .env.sample             # guia das variáveis (versionado)
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## Padrões de desenvolvimento

Veja [`api/docs/padroes_de_desenvolvimento.md`](api/docs/padroes_de_desenvolvimento.md) para Conventional Commits, padrão de branches, organização de imports e logs.

## Licença

Apache 2.0
