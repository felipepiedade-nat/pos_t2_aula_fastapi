 # APIs da Aula — Pós-Graduação UFG-CEIA

  API educacional desenvolvida na disciplina **Construção de APIs para IA** da Pós-Graduação em Sistemas e Agentes
  Inteligentes (UFG-CEIA).

  **Autor:** Felipe Piedade

  ## O que essa API faz

  - **Operações matemáticas** em 3 formatos diferentes (path params, query params, Pydantic BaseModel)
  - **Operação matemática genérica** com Enum (soma, subtração, multiplicação, divisão)
  - **Geração de histórias** usando LLM (Groq + Llama 3.1)
  - **Autenticação global** via token simples
  - **Validação automática** com Pydantic + HTTPException customizadas
  - **Logging estruturado** com níveis INFO/WARNING

  ## Requisitos

  - Python 3.12+
  - [uv](https://docs.astral.sh/uv/) instalado
  - Chave de API do Groq (gratuita em https://console.groq.com/)

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

  3. Crie um arquivo `.env` na raiz com sua chave do Groq:
     ```env
     GROQ_API_KEY=gsk_sua_chave_aqui
     ```

  ## Executar localmente

  ```bash
  uv run fastapi dev
  ```

  A aplicação fica disponível em:

  - API: http://localhost:8000
  - Swagger UI: http://localhost:8000/docs?api_token=123
  - Redoc: http://localhost:8000/redoc?api_token=123

  > ⚠️ Todos os endpoints exigem o query parameter `?api_token=123` (token didático).

  ## Endpoints

  | Método | Endpoint | Descrição |
  |---|---|---|
  | GET | `/teste` | Hello World |
  | GET | `/soma/v1/{n1}/{n2}` | Soma via path params (deprecated) |
  | POST | `/soma/v2` | Soma via query params |
  | POST | `/soma/v3` | Soma via Pydantic BaseModel |
  | POST | `/operacao_matematica` | Operação genérica (soma/sub/mult/div) |
  | POST | `/gerar_historia` | Gera história usando LLM (Groq) |

  ## Stack

  - **FastAPI** — framework web
  - **Pydantic** — validação de dados
  - **uv** — gerenciador de pacotes
  - **Groq + Llama 3.1** — LLM para geração de texto
  - **python-dotenv** — variáveis de ambiente
  - **Ruff** — linter e formatter
  - **Logging** — biblioteca nativa do Python

  ## Estrutura do projeto

  ```
  pos_t2_aula_fastapi/
  ├── main.py             # Aplicação FastAPI + todos os endpoints
  ├── pyproject.toml      # Manifesto do projeto
  ├── uv.lock             # Versões resolvidas
  ├── .env                # Variáveis de ambiente (não versionado)
  ├── .gitignore
  └── README.md
  ```

  ## Licença

  Apache 2.0