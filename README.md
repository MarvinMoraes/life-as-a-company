# life-as-a-company

**Uma fábrica de SaaS agêntica e reutilizável.** Recebe uma ideia, passa por discovery, valida mercado, gera PRD, projeta a arquitetura, revisa com QA e registra tudo em memória Obsidian — com disciplina máxima de tokens.

---

## O que é isso

Uma plataforma-base multiagente para operar como uma empresa de software de uma pessoa só. Cinco agentes especializados colaboram sob orquestração central para transformar ideias em produtos definidos, planejados e documentados — sem desperdício de contexto.

```
Ideia bruta
    → Manager (interpreta e delega)
    → Product Strategist (discovery + PRD)
    → Marketing Strategist (mercado + GTM)
    → QA (revisão + aprovação)
    → Engineer (arquitetura + plano técnico)
    → Vault Obsidian (memória viva)
```

---

## Os 5 Agentes

| Agente | Papel | Entrega |
|--------|-------|---------|
| **Manager** | Orquestra, delega, controla contexto | Planos, decisões, snapshots |
| **Product Strategist** | Discovery, personas, escopo | PRD completo |
| **Senior Engineer** | Arquitetura, stack, código | TechnicalPlan |
| **Marketing Strategist** | Mercado, posicionamento, GTM | MarketingPlan |
| **QA** | Revisão, veredictos, achados | QAEvaluation |

Cada agente tem: prompt de sistema dedicado, política de tokens, formato de saída estruturado e política de memória própria. Agentes não se comunicam diretamente — tudo passa pelo Manager.

---

## Workflows

### A — Idea → PRD
```
User → Manager → Product → Marketing → QA → Manager
```
Transforma uma ideia bruta em PRD aprovado com análise de mercado.

### B — PRD → Build
```
PRD → Manager → Engineer → QA → Manager
```
Gera plano técnico completo a partir de um PRD aprovado.

### C — Product Improvement
```
Feedback → Manager → Product + Marketing → Engineer → QA
```
Processa feedback de usuários e gera delta de produto priorizado.

### D — Project Audit
```
Manager → QA → Product → Engineer → Manager
```
Auditoria completa do estado atual de qualquer projeto.

---

## Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/life-as-a-company.git
cd life-as-a-company

# 2. Crie ambiente virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# 3. Instale dependências
pip install -e ".[dev]"

# 4. Configure variáveis de ambiente
cp .env.example .env
# Edite .env conforme necessário
```

---

## Como Usar

### Via CLI

```bash
# Workflow A: Ideia → PRD (com mock provider)
factory idea "App de gestão de tarefas para times remotos" --project taskflow-saas

# Com Claude API
factory idea "Seu produto aqui" --project meu-projeto --provider claude

# Workflow D: Auditoria
factory audit taskflow-saas --scope full

# Ver agentes registrados
factory agents
```

### Via Python

```python
import asyncio
from src.orchestrator.manager import Orchestrator
from src.workflows.idea_to_prd import run_idea_to_prd

async def main():
    orchestrator = Orchestrator(vault_path="./vault")

    snapshot = await run_idea_to_prd(
        orchestrator=orchestrator,
        project_id="meu-saas",
        raw_idea="Plataforma de cursos online focada em desenvolvedores",
        target_audience="Devs plenos e seniors em transição de carreira",
    )

    print(f"Status: {snapshot.status}")
    print(f"Steps: {snapshot.steps_completed}")
    print(f"Tokens usados: {snapshot.token_budget_used}")

asyncio.run(main())
```

### Tarefa Avulsa

```python
from src.orchestrator.manager import Orchestrator
from src.schemas.task import AgentRole

async def main():
    orch = Orchestrator()

    # Invocar qualquer agente diretamente
    response = await orch.run_task(
        role=AgentRole.PRODUCT,
        objective="Criar PRD para marketplace de freelancers",
        project_id="freela-hub",
        depth="deep",
    )
    print(response.summary)
    print(response.content)
```

---

## Memória em Obsidian

Todo resultado significativo é salvo como nota markdown no vault. Abra o vault no Obsidian para visualizar o grafo de conhecimento dos seus projetos.

```
vault/
  _system/          → princípios e registry de agentes
  Projects/         → nota-mestre por projeto
  PRDs/             → PRDs versionados
  Decisions/        → ADRs e decisões importantes
  Research/         → análises de mercado
  Marketing/        → planos GTM
  QA/               → relatórios de revisão
  Agents/           → logs por agente
  Snapshots/        → histórico de execuções
  Templates/        → templates para novas notas
```

### Frontmatter padrão de cada nota

```yaml
---
slug: taskflow-saas-prd-v1
title: "PRD: TaskFlow SaaS v1.0"
type: prd
project_id: taskflow-saas
tags: [prd, taskflow-saas]
summary: "PRD v1.0 com 4 features MVP para gestão inteligente de tarefas"
created: 2026-06-05
---
```

---

## Eficiência de Tokens

A fábrica é desenhada para minimizar tokens sem perder qualidade de coordenação.

**Princípios:**
- Cada agente recebe apenas o contexto mínimo para sua tarefa
- Histórico completo nunca é carregado — apenas resumos progressivos
- Notas do vault entram como `summary` (~150 tokens), não como conteúdo completo
- `depth: short | medium | deep` controla verbosidade da resposta
- Manager é o guardião: verifica vault antes de criar nova tarefa

**Camadas de contexto por chamada (máx. 4.096 tokens):**

```
[task]    400 tokens  → objetivo + critérios de aceite
[agent]   200 tokens  → papel e responsabilidades
[project] 500 tokens  → visão + PRD + status (quando necessário)
[memory]  600 tokens  → notas seletivas do vault
[global]  300 tokens  → princípios gerais (se couber)
```

Ver [docs/token_governance.md](docs/token_governance.md) para detalhes.

---

## Estrutura do Projeto

```
life-as-a-company/
  src/
    core/           → BaseAgent, Registry, ContextGovernor
    orchestrator/   → Orchestrator (coordenador central)
    agents/         → 5 implementações de agente
    prompts/        → system prompts em markdown
    schemas/        → contratos Pydantic (ProjectBrief, PRD, etc.)
    workflows/      → 4 workflows prontos para uso
    memory/         → MemoryManager + ContextCompressor
    obsidian/       → Writer + Reader do vault
    providers/      → Mock + Claude + factory
    config/         → Settings via pydantic-settings
    utils/          → token counter, formatters
    cli.py          → CLI com Typer
  vault/            → Obsidian vault com templates e notas do sistema
  examples/
    taskflow_saas/  → exemplo ponta a ponta completo
  tests/            → smoke tests e testes de integração
  docs/             → arquitetura e governança de tokens
```

---

## Exemplo: TaskFlow SaaS

Exemplo completo em [`examples/taskflow_saas/`](examples/taskflow_saas/):

```bash
# Rodar o exemplo completo (mock provider, sem API)
python -m examples.taskflow_saas.run_example
```

Inclui:
- [`artifacts/prd_v1.json`](examples/taskflow_saas/artifacts/prd_v1.json) — PRD completo do TaskFlow
- [`artifacts/technical_plan_v1.json`](examples/taskflow_saas/artifacts/technical_plan_v1.json) — Plano técnico
- [`vault/`](examples/taskflow_saas/vault/) — Vault com nota de projeto gerada

---

## Providers

| Provider | Quando usar | Config |
|----------|-------------|--------|
| `mock` | Desenvolvimento, CI/CD, testes | Padrão, sem config |
| `claude` | Produção com Claude | `ANTHROPIC_API_KEY` no `.env` |
| `openai` | *Em breve* | `OPENAI_API_KEY` no `.env` |

```bash
# Desenvolvimento (padrão)
DEFAULT_PROVIDER=mock

# Produção
DEFAULT_PROVIDER=claude
DEFAULT_MODEL=claude-sonnet-4-6
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Testes

```bash
# Rodar todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=term-missing

# Só smoke tests
pytest tests/test_smoke.py -v
```

---

## Integração com n8n (Fase 2)

A arquitetura está preparada para integração com n8n:

- Cada workflow pode ser exposto como webhook trigger
- `AgentResponse` e `ExecutionSnapshot` são schemas JSON prontos para nós n8n
- O vault Obsidian pode ser sincronizado via n8n com Notion, Google Drive, etc.
- Providers podem ser adicionados via nós HTTP Request do n8n

---

## Roadmap

### Fase 1 (atual)
- [x] 5 agentes com prompts reais
- [x] 4 workflows principais
- [x] Memória em Obsidian markdown
- [x] Mock provider para desenvolvimento
- [x] Claude API provider
- [x] CLI com Typer
- [x] Schemas Pydantic completos
- [x] Smoke tests

### Fase 2
- [ ] OpenAI provider
- [ ] Busca semântica na memória (embeddings)
- [ ] Interface web básica
- [ ] Integração n8n (webhooks)
- [ ] Prompt caching (Claude API)
- [ ] Novos agentes: Finance, Legal, Design
- [ ] Multi-project dashboard
- [ ] Export para Notion

---

## Arquitetura

Ver [docs/architecture.md](docs/architecture.md) para diagramas Mermaid e detalhes de cada componente.

---

*Construído com Python 3.11 + Pydantic v2 + FastAPI ecosystem*
*Memória em Obsidian · Providers plugáveis · Pronto para n8n*
