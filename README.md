# life-as-a-company

**Uma fábrica de SaaS agêntica.** Cinco agentes especializados que orquestram, planejam, codificam, pesquisam e revisam — com tool use real, memória em Obsidian e disciplina máxima de tokens.

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Runtime | Python 3.11+ |
| LLM | Anthropic Claude — roteamento por papel (Opus 4.8 / Sonnet 5 / Haiku 4.5) |
| Tool Use | Anthropic function calling + MCP servers |
| Schemas | Pydantic v2 |
| Memória | Obsidian markdown (vault local) |
| CLI | Rich + Typer |
| Async | asyncio + aiofiles |
| Testes | pytest + pytest-asyncio |
| Linter | Ruff |

### MCPs Suportados (opcionais)

| MCP | Agentes | Tools |
|-----|---------|-------|
| `@modelcontextprotocol/server-github` | Manager, Engineer | `github_list_issues`, `github_create_pull_request`, `github_search_code` |
| `@modelcontextprotocol/server-brave-search` | Product, Marketing | `web_search` |
| `@modelcontextprotocol/server-sequential-thinking` | todos | raciocínio estruturado |
| `@modelcontextprotocol/server-memory` | todos | grafo de entidades |
| `@modelcontextprotocol/server-git` | Engineer | `git_diff`, `git_log`, `git_status` |

---

## Os 5 Agentes

| Agente | Papel | Modelo (default) | Tools |
|--------|-------|------------------|-------|
| **Manager** | Orquestra, delega, controla contexto | `claude-opus-4-8` | delegate, read/write vault, GitHub |
| **Product** | Discovery, PRD, personas, roadmap | `claude-sonnet-5` | read/write vault, web_search |
| **Engineer** | Arquitetura, código real, PRs | `claude-sonnet-5` | read/write/list flouwy, GitHub, git |
| **Marketing** | Mercado, posicionamento, GTM | `claude-haiku-4-5` | read/write vault, web_search |
| **QA** | Revisão, lint, build, veredictos | `claude-haiku-4-5` | read flouwy, npm run lint/build |

Agentes não se comunicam diretamente — tudo passa pelo Manager via closure `_agent_caller`.

### Model Routing por Papel

Cada agente roda no modelo adequado ao seu trabalho: **orquestração** no modelo mais forte, **execução** de código/specs num modelo intermediário, e tarefas mais simples num modelo econômico. Isso equilibra qualidade e custo automaticamente.

| Papel | Modelo | Racional |
|-------|--------|----------|
| Manager | Opus 4.8 (`MODEL_MANAGER`) | orquestração, planejamento, delegação |
| Engineer / Product | Sonnet 5 (`MODEL_ENGINEER` / `MODEL_PRODUCT`) | execução de código e specs |
| QA / Marketing | Haiku 4.5 (`MODEL_QA` / `MODEL_MARKETING`) | verificação e copy (alto volume) |

Todos configuráveis via `.env`. Sob o capô, `settings.model_for_role()` resolve o modelo e `ClaudeLLMProvider.for_model()` cria um provider-irmão reusando o mesmo client HTTP (sem recriar conexão por agente). A delegação Manager→outros herda o roteamento automaticamente.

---

## Organização do Repositório

```
life-as-a-company/
├── src/
│   ├── agents/          → 5 implementações de agente
│   ├── core/            → BaseAgent (loop agêntico), Registry, ContextGovernor
│   ├── events.py        → EventBus global pub/sub (Rich CLI)
│   ├── orchestrator/    → Orchestrator (ponto central)
│   ├── prompts/         → system prompts em markdown por agente
│   ├── providers/       → Mock + Claude + factory pattern
│   ├── schemas/         → contratos Pydantic (TaskBrief, AgentResponse, etc.)
│   ├── tools/           → ToolExecutor, tool definitions, MCPToolAdapter
│   ├── workflows/       → 5 workflows prontos
│   ├── memory/          → MemoryManager + ContextCompressor
│   ├── obsidian/        → Writer + Reader do vault
│   ├── config/          → Settings via pydantic-settings
│   └── utils/           → token counter, formatters
├── scripts/
│   ├── factory_cli.py   → Rich CLI principal (modos: chat, workflow, agent)
│   ├── chat_manager.py  → CLI legado (modo chat simples)
│   └── dev/             → scripts de debug/dev
├── vault/
│   ├── _system/         → FACTORY_PRINCIPLES.md, AGENT_REGISTRY.md, INDEX.md
│   └── Templates/       → templates de notas (prd, project, qa, etc.)
├── docs/
│   ├── architecture.md  → diagramas Mermaid e detalhes de cada componente
│   └── token_governance.md → política de tokens
├── tests/               → 21 testes (smoke, schemas, memory)
├── examples/
│   └── taskflow_saas/   → exemplo ponta a ponta com mock provider
└── pyproject.toml       → dependências e configuração
```

---

## Como Usar em Projetos Novos

### 1. Clone e configure o ambiente

```bash
git clone https://github.com/MarvinMoraes/life-as-a-company.git
cd life-as-a-company

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

pip install -e ".[claude,dev]"
```

### 2. Configure o `.env`

```bash
cp .env.example .env
```

Edite `.env`:

```env
DEFAULT_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...

# Opcional — MCPs adicionais
GITHUB_TOKEN=ghp_...
BRAVE_API_KEY=BSA...
```

### 3. (Opcional) Instale MCPs

```bash
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-brave-search
```

### 4. Crie o vault para o novo projeto

O vault é um diretório local que vira um cofre Obsidian. Configure o path em `.env` ou use o padrão `./vault`:

```env
VAULT_PATH=C:/Users/seu-usuario/Documents/laac
```

Abra no Obsidian: `File > Open Vault > selecione o diretório`.

### 5. Rode o Workflow A — Idea to PRD

```bash
python scripts/factory_cli.py --mode workflow --workflow idea-to-prd
# Input: "App de gestão de tarefas para times remotos"
```

Ou via Python:

```python
import asyncio
from src.orchestrator.manager import Orchestrator
from src.workflows.idea_to_prd import run_idea_to_prd

async def main():
    orch = Orchestrator(vault_path="./vault")
    snapshot = await run_idea_to_prd(
        orchestrator=orch,
        project_id="meu-saas",
        raw_idea="Plataforma de cursos online focada em desenvolvedores",
        target_audience="Devs plenos e seniors em transição de carreira",
    )
    print(f"Status: {snapshot.status}")
    print(f"Tokens: {snapshot.token_budget_used}")

asyncio.run(main())
```

### 6. Chat com o Manager

```bash
python scripts/factory_cli.py --mode chat --project meu-saas
```

O Manager usa tools em tempo real — você vê cada tool call colorido no terminal.

---

## Como Usar em Projetos Já Existentes (como Flouwy)

O Flouwy é um app Next.js já existente. A fábrica se conecta ao codebase real via `flouwy_path`.

### 1. Configure o path do projeto

Em `.env`:

```env
FLOUWY_PATH=C:/Users/MarcusMoraes/Documents/GitHub/flowly
```

Ou em `src/config/settings.py`, o default já aponta para `flowly`.

### 2. Rode um sprint de feature

```bash
python scripts/factory_cli.py --mode workflow --workflow flouwy-sprint
# Input: "Add loading spinner ao dashboard"
```

O que acontece:
1. **Manager** faz triage e monta plano
2. **Product** atualiza a spec da feature
3. **Engineer** usa `list_files` → `read_file` → `write_file` para implementar código real no repo `flowly`
4. **QA** executa `npm run lint` e `npm run build` — se falhar, reporta o erro com recomendação de fix

### 3. Tarefa direta num agente (modo `agent`)

Executa um único agente isolado, no modelo roteado do papel:

```bash
python scripts/factory_cli.py --mode agent --agent engineer \
  --objective "Refatorar src/components/flowly/Dashboard.tsx para usar shadcn Card"
```

`--agent` aceita `manager | engineer | product | marketing | qa`. Sem `--objective`, o CLI pergunta interativamente.

### 4. Via Python

```python
import asyncio
from src.orchestrator.manager import Orchestrator
from src.workflows.flouwy_sprint import run_flouwy_sprint

async def main():
    orch = Orchestrator(vault_path="C:/Users/MarcusMoraes/Documents/laac")
    snapshot = await run_flouwy_sprint(
        orchestrator=orch,
        feature_or_bug="Add empty state component to habits page",
        sprint_type="feature",
        project_id="flouwy",
    )
    print(snapshot.status)
    print(snapshot.artifacts)

asyncio.run(main())
```

### 5. Auditoria do projeto existente

```bash
python scripts/factory_cli.py --mode workflow --workflow project-audit --project flouwy
```

---

## Workflows Disponíveis

| Workflow | Comando CLI | Agentes envolvidos |
|----------|-------------|-------------------|
| Idea → PRD | `--workflow idea-to-prd` | Manager → Product → Marketing → QA |
| PRD → Build | `--workflow prd-to-build` | Manager → Engineer → QA |
| Product Improvement | `--workflow product-improvement` | Manager → Product + Marketing → Engineer → QA |
| Project Audit | `--workflow project-audit` | Manager → QA → Product → Engineer |
| Flouwy Sprint | `--workflow flouwy-sprint` | Manager → Product → Engineer → QA (com tools reais) |

---

## Testes

```bash
# Todos os testes (21 passando)
python -m pytest tests/ -v

# Com cobertura
pytest --cov=src --cov-report=term-missing

# Só smoke tests
pytest tests/test_smoke.py -v
```

Testes usam mock provider automaticamente — sem custo de API.

---

## Providers

| Provider | Quando usar | Config |
|----------|-------------|--------|
| `mock` | Desenvolvimento, CI/CD, testes | Padrão, sem config |
| `claude` | Produção, tool use real | `ANTHROPIC_API_KEY` no `.env` |

```env
# Dev (padrão)
DEFAULT_PROVIDER=mock

# Produção
DEFAULT_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...

# Model routing por papel (defaults abaixo — ajuste conforme custo/qualidade)
DEFAULT_MODEL=claude-sonnet-5
MODEL_MANAGER=claude-opus-4-8
MODEL_ENGINEER=claude-sonnet-5
MODEL_PRODUCT=claude-sonnet-5
MODEL_QA=claude-haiku-4-5
MODEL_MARKETING=claude-haiku-4-5
```

---

## Memória em Obsidian

Todo resultado significativo é salvo como nota markdown no vault. Abra no Obsidian para visualizar o grafo de conhecimento dos projetos.

O `ContextGovernor` injeta memória em cada tarefa: o perfil do usuário (`vault/_system/MARCUS.md`) e os princípios da fábrica (`vault/_system/FACTORY_PRINCIPLES.md`) entram como camadas de contexto, e notas relevantes são recuperadas por slug exato (`memory_hints`) ou, na ausência delas, por busca de relevância no vault.

Ver `vault/INDEX.md` para a estrutura completa e convenções de naming.

---

## Arquitetura

Ver [`docs/architecture.md`](docs/architecture.md) para diagramas Mermaid detalhados do loop agêntico, EventBus, ToolExecutor e camada de MCPs.

---

## Versão Atual: 0.2.0

- [x] 5 agentes com prompts dedicados e tool use real
- [x] Model routing por papel (Opus 4.8 / Sonnet 5 / Haiku 4.5, configurável no `.env`)
- [x] 5 workflows (incluindo Flouwy Sprint) — todos acessíveis pela CLI
- [x] 3 modos de CLI: `chat`, `workflow`, `agent`
- [x] Loop agêntico (LLM → tool → LLM → end_turn)
- [x] Contexto `_system` (MARCUS.md + FACTORY_PRINCIPLES.md) injetado por tarefa
- [x] Prompt caching Claude API (~90% custo em cache hits)
- [x] MCPs: GitHub, Brave Search, sequential-thinking, memory, git
- [x] EventBus pub/sub + Rich CLI com cores por agente
- [x] Segurança de paths por role (sem traversal)
- [x] Mock provider para dev/CI sem API key
- [x] 21 testes passando

---

*Python 3.11 · Pydantic v2 · Anthropic Claude · Obsidian vault · MCPs opcionais*
