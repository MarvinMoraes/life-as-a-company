---
title: "LAAC — Life as a Company: Índice de Conceitos"
type: index
version: "2.0"
updated: 2026-06-17
tags:
  - index
  - laac
  - concepts
---

# LAAC — Life as a Company

> *Tratar projetos pessoais com a disciplina de uma empresa de software.*

---

## O que é LAAC?

LAAC é uma filosofia operacional e uma plataforma técnica. A ideia central: uma pessoa pode operar com a disciplina de uma empresa inteira usando agentes de IA especializados que colaboram sob orquestração central.

Ao invés de largar tudo num único prompt gigante, você separa responsabilidades:
- Um agente pensa em produto
- Um pensa em mercado
- Um codifica
- Um revisa
- Um coordena tudo

Cada um tem papel fixo, política de tokens própria e memória estruturada em Obsidian.

---

## Os 5 Agentes

```
Manager            → orquestra, delega, nunca deixa contexto vazar
Product Strategist → discovery, PRD, personas, roadmap
Senior Engineer    → arquitetura, código real, pull requests
Marketing          → mercado, posicionamento, GTM
QA                 → revisão, lint, build, veredictos
```

Agentes **não se comunicam diretamente**. Tudo passa pelo Manager. O Manager usa uma closure `_agent_caller` para delegar sem criar imports circulares no código.

---

## Workflows Prontos

### A — Idea to PRD
```
User → Manager → Product → Marketing → QA → Manager
```
Transforma uma ideia bruta em PRD aprovado com análise de mercado.

### B — PRD to Build
```
PRD → Manager → Engineer → QA → Manager
```
Gera plano técnico a partir de um PRD aprovado.

### C — Product Improvement
```
Feedback → Manager → Product + Marketing → Engineer → QA
```
Processa feedback e gera delta de produto priorizado.

### D — Project Audit
```
Manager → QA → Product → Engineer → Manager
```
Auditoria completa do estado atual de um projeto.

### E — Flouwy Sprint (Fase 2)
```
Manager (triage) → Product (spec) → Engineer (implementa código real) → QA (lint + build)
```
Sprint de feature ou bugfix no app Flouwy — com escrita real de arquivos.

---

## Como os Agentes Executam Tarefas Reais (Fase 2)

### Loop Agêntico

```
LLM retorna → stop_reason == "tool_use"
    → ToolExecutor.execute(tool_name, tool_input)
    → resultado → messages → LLM → ...
    → stop_reason == "end_turn" → done
```

Máximo de 10 iterações por tarefa. O EventBus emite eventos a cada tool call para o Rich CLI exibir em tempo real.

### Camada de Tools

```
Native (Anthropic function calling)        MCP (subprocesso stdio)
─────────────────────────────────          ─────────────────────────
read_file    → lê arquivo com path check   github    → PRs, issues, search
write_file   → escreve com path check      brave     → web_search
list_files   → lista diretório             sequential-thinking → raciocínio
run_command  → allowlist: lint/build/dev   memory    → grafo de entidades
delegate_to_agent → Manager delega         git       → diff, log, status
```

MCPs são **opcionais** — graceful degradation se não estiverem instalados ou sem credenciais.

### Segurança de Paths

Cada role tem um root permitido. Qualquer tentativa de `../` traversal retorna `PermissionError`:

| Role | Pode ler | Pode escrever |
|------|----------|---------------|
| Manager | vault | vault |
| Engineer | flouwy | flouwy |
| Product | vault + flouwy | vault |
| Marketing | vault | vault |
| QA | flouwy | — |

---

## Prompt Caching

System prompts ≥ 1024 tokens recebem `cache_control: {type: ephemeral}` automaticamente quando o provider é Claude. Cache TTL = 5 minutos. Resultado: ~90% de redução de custo em cache hits para tasks repetitivas.

```python
# ClaudeProvider adiciona automaticamente:
[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}]
```

---

## Memória em Obsidian

O vault é a memória viva dos projetos. Tudo o que um agente decide ou entrega de relevância é salvo como nota markdown com frontmatter YAML.

```
vault/
  _system/    → FACTORY_PRINCIPLES.md, AGENT_REGISTRY.md, INDEX.md (este arquivo)
  Projects/   → {project-id}-project.md (nota-mestre)
  PRDs/       → {project-id}-prd-v{N}.md
  Decisions/  → {project-id}-adr-{NNN}.md
  Research/   → {project-id}-research-{topic}.md
  Marketing/  → {project-id}-marketing-plan.md
  QA/         → {project-id}-qa-{artifact}.md
  Snapshots/  → snap-{id}.md
  Templates/  → templates de cada tipo de nota
```

### Frontmatter padrão

```yaml
---
slug: flouwy-prd-v1
title: "PRD: Flouwy v1.0"
type: prd
project_id: flouwy
tags: [prd, flouwy]
summary: "PRD v1.0 do app Flouwy — check-ins, hábitos, gamificação"
created: 2026-06-17
---
```

---

## SDD — Specification-Driven Development

Os agentes lêem a spec (PRD) antes de agir. O Product Agent é o guardião da spec. Nenhum Engineer codifica sem PRD aprovado pelo QA. Isso evita scope creep e garante que o que é construído é o que foi decidido.

---

## Disciplina de Tokens

```
Context pack por chamada (máx. 4.096 tokens):

  [task]    400 tokens  → objetivo + critérios de aceite
  [agent]   200 tokens  → papel e responsabilidades
  [project] 500 tokens  → visão + PRD + status (quando necessário)
  [memory]  600 tokens  → notas seletivas do vault (memory_hints)
  [global]  300 tokens  → princípios gerais (se couber)
```

O Manager nunca carrega o vault inteiro — usa `memory_hints` (slugs) para buscar só o que é relevante. Histórico completo nunca é injetado, apenas resumos progressivos.

---

## CLI — Modos de Uso

```bash
# Chat com Manager (tools habilitadas)
python scripts/factory_cli.py --mode chat --project flouwy

# Sprint Flouwy (workflow completo)
python scripts/factory_cli.py --mode workflow --workflow flouwy-sprint

# Tarefa direta num agente específico
python scripts/factory_cli.py --mode agent --role engineer
```

Display Rich: cores por agente (Manager=azul, Engineer=verde, Product=amarelo, QA=vermelho, Marketing=magenta), log de tool calls em tempo real, 8fps.

---

## Projetos Ativos

| Projeto | Path | Stack | Status |
|---------|------|-------|--------|
| Flouwy | `C:/Users/MarcusMoraes/Documents/GitHub/flowly` | Next.js 16, React 19, Supabase, TailwindCSS 4, shadcn/ui | MVP ativo |

---

## Versão

- **Fase 1 (0.1.0):** 5 agentes, 4 workflows, vault Obsidian, mock provider, CLI Typer
- **Fase 2 (0.2.0):** Tool use real (Anthropic), loop agêntico, prompt caching, MCPs, Rich CLI, workflow Flouwy Sprint
