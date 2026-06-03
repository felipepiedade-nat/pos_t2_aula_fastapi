# Padrões de Desenvolvimento

Este documento centraliza as convenções adotadas no repositório.

## Estrutura de pastas

```
pos_t2_aula_fastapi/
├── api/
│   ├── main.py             # instancia FastAPI + include_router
│   ├── models.py           # BaseModels (Pydantic) e Enums
│   ├── utils.py            # logger, autenticação, gateway da LLM
│   ├── docs/               # documentação interna do código
│   └── routers/
│       ├── llm_router.py
│       └── operacoes_router.py
├── docs/                   # documentação do projeto (padrões, decisões)
├── .env                    # segredos reais (ignorado pelo Git)
├── .env.sample             # guia das variáveis (versionado)
├── pyproject.toml
├── README.md
└── uv.lock
```

## Princípio da responsabilidade única

Cada arquivo tem **uma única responsabilidade**:

- `main.py` apenas instancia o FastAPI e inclui os routers.
- `models.py` apenas declara `BaseModel` e `Enum`.
- `utils.py` apenas centraliza funções reutilizáveis (logger, autenticação, chamada à LLM).
- `routers/*.py` apenas declaram endpoints — sem lógica pesada inline.

## Conventional Commits

Mensagens de commit seguem `tipo(escopo opcional): descrição no imperativo`.

| Tipo | Quando usar |
|---|---|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `hotfix` | Correção urgente em produção |
| `refactor` | Mudança interna sem alterar comportamento externo |
| `style` | Formatação, espaços, ponto-e-vírgula (Ruff) |
| `docs` | Documentação (README, docstrings, este arquivo) |
| `test` | Testes |
| `chore` | Build, CI, dependências, configs |
| `perf` | Performance |

Referência: <https://www.conventionalcommits.org>

## Padrão de branches

```
tipo/#numero-da-issue/descricao-breve-em-kebab
```

Exemplos:

- `feat/#12/endpoint-classificar-email`
- `fix/#7/divisao-por-zero-no-router`
- `refactor/#3/centraliza-logger-em-utils`

## Imports

- Sempre **explícitos**: `from models import Historia` — nunca `from models import *`.
- Imports rodam a partir da pasta `api/`. A aplicação sobe com `uv run fastapi dev api/main.py` da raiz do projeto.

## Logs

- Logger criado via `get_logger()` em `utils.py` — não chamar `logging.basicConfig` em outros lugares.
- `info` para eventos de negócio (requisição recebida, operação concluída).
- `warning` para tentativas inválidas (token errado, divisão por zero).
- Evitar logar conteúdo gerado pela LLM em `info` — usar `debug` se necessário.

## Variáveis de ambiente

- Toda chave/credencial vive em `.env`.
- `.env` está no `.gitignore`; nunca commitado.
- `.env.sample` é versionado e documenta as variáveis necessárias.
- Carregamento via `load_dotenv(find_dotenv())` para funcionar tanto em `fastapi dev` quanto em `fastapi run`.

## Formatação

```bash
uv run ruff format        # formata todos os arquivos
uv run ruff check         # checagem estática
uv run ruff check --fix   # corrige o que dá automaticamente
```
