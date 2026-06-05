---
name: project-saas-factory
description: SaaS Factory multiagente — arquitetura, agentes, workflows e vault Obsidian implementados no repo life-as-a-company
metadata:
  type: project
---

SaaS Factory está implementada em `C:\Users\MarcusMoraes\Documents\GitHub\life-as-a-company`.

**Why:** Plataforma pessoal para operar como fábrica de SaaS — idea-to-product com 5 agentes especializados.

**How to apply:** Ao trabalhar neste repo, ter em mente que a arquitetura central é o Orchestrator em `src/orchestrator/manager.py`. Agentes em `src/agents/`. Workflows em `src/workflows/`. Memória em `vault/`.

## Estrutura principal

- `src/orchestrator/manager.py` — Orchestrator central (ponto de entrada programático)
- `src/agents/` — 5 agentes: manager, engineer, product, marketing, qa
- `src/prompts/*.md` — system prompts dos agentes (um arquivo por agente)
- `src/schemas/` — contratos Pydantic completos
- `src/workflows/` — 4 workflows: idea_to_prd, prd_to_build, product_improvement, project_audit
- `src/memory/` + `src/obsidian/` — camada de memória markdown
- `src/providers/` — mock + claude + factory pattern
- `src/cli.py` — CLI com Typer
- `vault/` — Obsidian vault com templates e notas do sistema
- `examples/taskflow_saas/` — exemplo completo ponta a ponta
- `tests/` — 21 testes (smoke + schemas + memory), todos passando

## Provider atual
`DEFAULT_PROVIDER=mock` por padrão. Para usar Claude API, setar `ANTHROPIC_API_KEY` e `DEFAULT_PROVIDER=claude` no `.env`.

## Status
Fase 1 completa e testada. 21/21 testes passando. Exemplo end-to-end funcional.
