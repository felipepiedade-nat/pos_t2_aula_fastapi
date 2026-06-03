# APIs da Aula — Pós-Graduação UFG-CEIA

API educacional desenvolvida na disciplina **Construção de APIs para IA** da Pós-Graduação em Sistemas e Agentes Inteligentes (UFG-CEIA).

**Autor:** Felipe Piedade

## O que essa API faz

### Endpoints de IA do trabalho final

- **`POST /api/v1/juridico/classificar_peticao`** — recebe o texto de uma petição inicial e classifica em uma das 15 áreas do Direito brasileiro (Enum), devolvendo a área identificada + justificativa.
- **`POST /api/v1/juridico/extrair_pedidos`** — recebe o texto de uma petição inicial e devolve a lista objetiva dos pedidos formulados ao juiz.

Ambos usam **Groq + Llama 3.1** com `response_format=json_object` para garantir saída JSON sintaticamente válida.

### Endpoints de apoio (vindos da Aula 2)

- Operações matemáticas em 3 formatos (path params, query params, Pydantic `BaseModel`)
- Operação matemática genérica com `Enum` (soma, subtração, multiplicação, divisão)
- `gerar_historia` marcado como **deprecated** (mantido como referência da Aula 2)

## Boas práticas aplicadas

- ✅ **Versionamento de API** com prefixo `/api/v1/`
- ✅ **Autenticação Bearer Token** via header `Authorization: Bearer <token>`
- ✅ **Validação Pydantic** com `Field` (limites de tamanho, descrição, exemplos)
- ✅ **`response_model`** declarado em todos os endpoints
- ✅ **Enum** para conjuntos fechados (áreas do Direito, tipos de operação)
- ✅ **Exception handlers globais** padronizando 422, 401, 500 em JSON consistente
- ✅ **Logging estruturado** com rotação automática (console + `app.log` + `erros.log`)
- ✅ **`.env`** + **`.env.sample`** para gestão de segredos
- ✅ **Estrutura modular** em routers separados por domínio
- ✅ **Docstrings** estilo Google em todas as funções públicas

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

3. Crie um arquivo `.env` a partir do `.env.sample` e preencha:

   ```env
   GROQ_API_KEY=gsk_sua_chave_groq_aqui
   API_TOKEN=defina_um_token_qualquer
   ```

## Executar localmente

```bash
uv run fastapi dev api/main.py
```

A aplicação fica disponível em:

| URL | O que é |
|---|---|
| <http://127.0.0.1:8000/> | Status simples (`{"status": "ok"}`) |
| <http://127.0.0.1:8000/teste> | Endpoint público, sem autenticação |
| <http://127.0.0.1:8000/docs> | **Swagger UI** (interface interativa) |
| <http://127.0.0.1:8000/redoc> | Redoc (documentação alternativa) |
| <http://127.0.0.1:8000/openapi.json> | Especificação OpenAPI bruta |

### Como autenticar no Swagger

1. Abra <http://127.0.0.1:8000/docs>
2. Clique no botão **Authorize** (cadeado, canto superior direito)
3. Cole o valor do `API_TOKEN` configurado no `.env` (campo "Value")
4. **Authorize** → **Close**
5. Todos os endpoints sob `/api/v1/` agora vão receber o header automaticamente

### Como autenticar via `curl` (PowerShell)

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/v1/juridico/classificar_peticao" `
  -H "Authorization: Bearer SEU_TOKEN_AQUI" `
  -H "Content-Type: application/json" `
  -d '{"texto": "Excelentissimo Senhor Doutor Juiz de Direito da Vara do Trabalho..."}'
```

## Endpoints

### Públicos (sem autenticação)

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/` | Status simples |
| GET | `/teste` | Hello World |

### Sob `/api/v1/` (exigem Bearer Token)

#### Jurídico (endpoints do trabalho final)

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/v1/juridico/classificar_peticao` | Classifica uma petição em 1 das 15 áreas do Direito |
| POST | `/api/v1/juridico/extrair_pedidos` | Extrai a lista de pedidos formulados na petição |

#### Operações matemáticas (Aula 2)

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/operacoes/soma/v1/{n1}/{n2}` | Soma via path params (deprecated) |
| POST | `/api/v1/operacoes/soma/v2` | Soma via query params |
| POST | `/api/v1/operacoes/soma/v3` | Soma via Pydantic BaseModel |
| POST | `/api/v1/operacoes/operacao_matematica` | Operação genérica via Enum |

#### LLM (deprecated)

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/v1/llm/gerar_historia` | Geração de história (Aula 2 — deprecated) |

## Exemplo de uso — classificar petição

**Request:**

```http
POST /api/v1/juridico/classificar_peticao HTTP/1.1
Authorization: Bearer SEU_TOKEN
Content-Type: application/json

{
  "texto": "Excelentíssimo Senhor Doutor Juiz de Direito da Vara do Trabalho de Goiânia. JOÃO DA SILVA, brasileiro, casado, motorista, vem propor a presente RECLAMAÇÃO TRABALHISTA em face da empresa TRANSPORTES XYZ LTDA. O reclamante foi admitido em 10/01/2022 e dispensado sem justa causa em 15/03/2025, sem o recebimento das verbas rescisórias devidas."
}
```

**Response (200 OK):**

```json
{
  "area": "trabalhista",
  "justificativa": "O texto faz referência expressa à Vara do Trabalho, ao reclamante, à reclamação trabalhista e às verbas rescisórias — termos típicos do Direito do Trabalho."
}
```

## Códigos de resposta

| Código | Significado | Quando aparece |
|---|---|---|
| 200 | OK | Requisição bem-sucedida |
| 201 | Created | Sucesso em `/operacoes/soma/v3` |
| 401 | Unauthorized | Token Bearer ausente ou inválido |
| 422 | Unprocessable Entity | Falha de validação Pydantic (texto curto demais, tipo errado, etc.) |
| 500 | Internal Server Error | Erro inesperado — sempre registrado em `logs/erros.log` |

## Logs

A API escreve em três destinos simultaneamente:

- **Console** (terminal onde `uv run fastapi dev` está rodando)
- **`logs/app.log`** — registro completo (rotação automática: 1 MB × 5 backups)
- **`logs/erros.log`** — apenas eventos `ERROR` ou superior, para auditoria

A pasta `logs/` é criada automaticamente no primeiro `boot` e está ignorada pelo Git.

## Stack

- **FastAPI** — framework web
- **Pydantic** — validação de dados
- **uv** — gerenciador de pacotes
- **Groq + Llama 3.1** — LLM para classificação e extração
- **python-dotenv** — variáveis de ambiente
- **Ruff** — linter e formatter

## Estrutura do projeto

```
pos_t2_aula_fastapi/
├── api/
│   ├── main.py                       # instancia FastAPI, exception handlers, include_router
│   ├── models.py                     # BaseModels e Enums (Pydantic)
│   ├── utils.py                      # logger, autenticação Bearer, gateway da LLM
│   ├── docs/
│   │   └── padroes_de_desenvolvimento.md
│   └── routers/
│       ├── juridico_router.py        # classificar_peticao + extrair_pedidos
│       ├── operacoes_router.py       # somas e operação matemática genérica
│       └── llm_router.py             # gerar_historia (deprecated)
├── logs/                             # gerada em runtime (não versionada)
├── .env                              # segredos reais (NÃO versionado)
├── .env.sample                       # guia das variáveis (versionado)
├── .github/
│   └── pull_request_template.md
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## Padrões de desenvolvimento

Veja [`api/docs/padroes_de_desenvolvimento.md`](api/docs/padroes_de_desenvolvimento.md) para:

- Conventional Commits
- Padrão de branches (`tipo/#issue/descricao`)
- Organização de imports e logs
- Comandos do Ruff

## Licença

Apache 2.0
