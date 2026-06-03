# APIs da Aula — Pós-Graduação UFG-CEIA

API educacional desenvolvida na disciplina **Construção de APIs para IA** da Pós-Graduação em Sistemas e Agentes Inteligentes (UFG-CEIA).

**Autor:** Felipe Piedade

## O que essa API faz

### Endpoints de IA do trabalho final

Cada operação (classificar e extrair) tem **duas versões coexistindo**, demonstrando versionamento real de API:

**v1 — texto colado** (JSON puro):

- `POST /api/v1/juridico/classificar_peticao` — classifica em 1 das 15 áreas do Direito
- `POST /api/v1/juridico/extrair_pedidos` — lista objetiva dos pedidos

**v2 — upload de arquivo** (multipart/form-data, aceita **.pdf** ou **.docx**):

- `POST /api/v2/juridico/classificar_peticao` — mesma classificação, a partir do arquivo
- `POST /api/v2/juridico/extrair_pedidos` — mesma extração, a partir do arquivo

Limites do v2: **5 MB** por arquivo, **50 páginas** (PDF), entre **50 e 12.000 caracteres** extraídos. Textos maiores são truncados em 12.000 caracteres para caber no limite de tokens/min do plano gratuito da Groq. PDFs escaneados (imagem, sem texto extraível) são rejeitados com 422.

### Limites da Groq (plano gratuito)

A API usa o modelo **`llama-3.1-8b-instant`** pela Groq, no plano **gratuito** (`on_demand` tier):

- **6.000 tokens por minuto** (TPM) — soma de prompt + resposta
- ~3 caracteres por token em português
- Por isso o limite de 12.000 caracteres extraídos por upload — deixa folga para o prompt + resposta caberem nos 6.000 TPM

Se receber HTTP **429** com mensagem de rate limit:

1. Aguarde 60 segundos e tente novamente, ou
2. Envie um documento menor, ou
3. Migre para o Dev Tier pago em <https://console.groq.com/settings/billing> para limite maior.

Todos usam **Groq + Llama 3.1** com `response_format=json_object` para garantir saída JSON sintaticamente válida.

### Endpoint de autenticação

- **`POST /api/v1/auth/token`** — recebe `usuario` e `senha`, devolve um **JWT** com expiração configurável (default: 1h).

### Endpoints de apoio (vindos da Aula 2)

- Operações matemáticas em 3 formatos (path params, query params, Pydantic `BaseModel`)
- Operação matemática genérica com `Enum` (soma, subtração, multiplicação, divisão)
- `gerar_historia` marcado como **deprecated** (mantido como referência da Aula 2)

## Boas práticas aplicadas

- ✅ **Versionamento real** com `v1` (texto) e `v2` (upload de arquivo) coexistindo
- ✅ **Upload de arquivos** (PDF/DOCX) com limites de tamanho, páginas e caracteres
- ✅ **Autenticação JWT real** com login → token assinado → expiração
- ✅ **Validação Pydantic** com `Field` (limites de tamanho, descrição, exemplos)
- ✅ **`response_model`** declarado em todos os endpoints
- ✅ **`responses={...}`** documentando 200/401/422/500 no Swagger
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

3. Crie um arquivo `.env` a partir do `.env.sample` e preencha as variáveis conforme a seção [Configurando variáveis de ambiente](#configurando-variáveis-de-ambiente) abaixo.

## Configurando variáveis de ambiente

A aplicação lê três variáveis do arquivo `.env`:

### `GROQ_API_KEY` (obrigatório)

Chave gratuita do Groq, provedor da LLM usada na classificação e extração. Cadastre em <https://console.groq.com/keys> → **Create API Key** → copie e cole como valor.

### `JWT_SECRET` (obrigatório)

Chave secreta usada pela API para **assinar criptograficamente** os tokens JWT emitidos no login. Cada desenvolvedor que rodar o projeto deve gerar **uma string aleatória própria, com no mínimo 32 caracteres**.

Para gerar uma chave segura, rode no PowerShell:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copie a saída e cole como valor de `JWT_SECRET`.

> ⚠️ **Se `JWT_SECRET` ou `GROQ_API_KEY` faltarem** (ou estiverem vazios), a aplicação **não sobe** e exibe mensagem clara apontando qual variável está ausente. Validação acontece na inicialização (fail-fast).

> 🛡️ **Nunca compartilhe** seu `JWT_SECRET` nem o commite no Git. Quem tem essa chave consegue forjar tokens válidos da sua API, como se fosse qualquer usuário cadastrado.

### `JWT_EXPIRA_SEGUNDOS` (opcional)

Tempo de vida dos JWTs emitidos no login. Default: `3600` (1 hora). Pode reduzir para 300 (5 min) em testes, ou aumentar conforme a sensibilidade do caso de uso.

## Usuários cadastrados (didático)

Os usuários e senhas estão **hardcoded** em `api/utils.py` para fins didáticos:

| Usuário | Senha |
|---|---|
| `felipe` | `123456` |
| `rogerio` | `123456` |

> ⚠️ **Em produção**, essa lista viria de um banco de dados com senhas hasheadas (bcrypt/argon2). Aqui é didático para que o avaliador possa testar sem cadastro.

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

## Fluxo de autenticação (JWT)

### Pelo Swagger

1. Abra <http://127.0.0.1:8000/docs>
2. Expanda **`POST /api/v1/auth/token`** → **Try it out**
3. Preencha:
   ```json
   {
     "usuario": "felipe",
     "senha": "123456"
   }
   ```
4. **Execute**. Copie o `access_token` retornado (string enorme começando com `eyJ...`).
5. Clique no botão **Authorize** (cadeado, topo direito) e cole o `access_token` no campo "Value".
6. **Authorize** → **Close**.
7. Pronto. Todas as demais rotas sob `/api/v1/` passam a aceitar o header `Authorization: Bearer <JWT>` automaticamente.

> 🕐 O JWT expira em **1 hora** (configurável em `JWT_EXPIRA_SEGUNDOS`). Quando expirar, repita o login.

### Via `curl` (PowerShell)

**1. Fazer login e capturar o token:**

```powershell
$resposta = curl.exe -s -X POST "http://127.0.0.1:8000/api/v1/auth/token" `
  -H "Content-Type: application/json" `
  -d '{"usuario": "felipe", "senha": "123456"}'

$token = ($resposta | ConvertFrom-Json).access_token
```

**2. Usar o token em uma rota protegida:**

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/v1/juridico/classificar_peticao" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"texto": "Excelentissimo Senhor Doutor Juiz de Direito da Vara do Trabalho..."}'
```

## Endpoints

### Públicos (sem autenticação)

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/` | Status simples |
| GET | `/teste` | Hello World |
| POST | `/api/v1/auth/token` | Login (devolve JWT) |

### Sob `/api/v1/` (exigem JWT no header)

#### Jurídico v1 — texto colado (endpoints do trabalho final)

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/v1/juridico/classificar_peticao` | Classifica petição (texto JSON) em 1 das 15 áreas |
| POST | `/api/v1/juridico/extrair_pedidos` | Extrai pedidos (texto JSON) |

#### Jurídico v2 — upload PDF/DOCX (endpoints do trabalho final)

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/v2/juridico/classificar_peticao` | Classifica petição via upload (.pdf ou .docx) |
| POST | `/api/v2/juridico/extrair_pedidos` | Extrai pedidos via upload (.pdf ou .docx) |

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
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
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

## Exemplo de uso — classificar via upload de arquivo (v2)

**Pelo Swagger:**

1. Expanda `POST /api/v2/juridico/classificar_peticao` → "Try it out"
2. No campo `arquivo`, clique em **Choose File** e selecione um `.pdf` ou `.docx`
3. **Execute** — a API extrai o texto do arquivo e devolve a classificação

**Via `curl` (PowerShell):**

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/v2/juridico/classificar_peticao" `
  -H "Authorization: Bearer $token" `
  -F "arquivo=@C:\caminho\para\peticao.pdf"
```

## Códigos de resposta

| Código | Significado | Quando aparece |
|---|---|---|
| 200 | OK | Requisição bem-sucedida |
| 201 | Created | Sucesso em `/operacoes/soma/v3` |
| 400 | Bad Request | Regra de negócio violada (divisão por zero, número negativo) |
| 401 | Unauthorized | JWT ausente, inválido ou expirado |
| 413 | Payload Too Large | Arquivo enviado no v2 excede 5 MB |
| 422 | Unprocessable Entity | Validação Pydantic, extensão não suportada, PDF sem texto, arquivo vazio |
| 429 | Too Many Requests | Limite de tokens/minuto da Groq atingido — aguarde alguns segundos |
| 500 | Internal Server Error | Erro inesperado — sempre registrado em `logs/erros.log` |
| 502 | Bad Gateway | Groq indisponível ou devolveu erro inesperado |

Cada endpoint declara explicitamente seus códigos de resposta via `responses={...}` no decorator, e o Swagger renderiza todos com descrição.

## Logs

A API escreve em três destinos simultaneamente:

- **Console** (terminal onde `uv run fastapi dev` está rodando)
- **`logs/app.log`** — registro completo (rotação automática: 1 MB × 5 backups)
- **`logs/erros.log`** — apenas eventos `ERROR` ou superior, para auditoria

A pasta `logs/` é criada automaticamente no primeiro boot e está ignorada pelo Git.

## Stack

- **FastAPI** — framework web
- **Pydantic** — validação de dados
- **PyJWT** — geração/validação de tokens JWT
- **uv** — gerenciador de pacotes
- **Groq + Llama 3.1** — LLM para classificação e extração
- **pypdf** — extração de texto de PDF
- **python-docx** — extração de texto de DOCX
- **python-dotenv** — variáveis de ambiente
- **Ruff** — linter e formatter

## Estrutura do projeto

```
pos_t2_aula_fastapi/
├── api/
│   ├── main.py                       # instancia FastAPI, exception handlers, include_router
│   ├── models.py                     # BaseModels e Enums (Pydantic)
│   ├── utils.py                      # logger, JWT, autenticação, gateway da LLM
│   ├── docs/
│   │   └── padroes_de_desenvolvimento.md
│   └── routers/
│       ├── auth_router.py            # login → JWT
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
