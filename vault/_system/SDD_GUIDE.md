---
slug: SDD_GUIDE
title: "Spec-Driven Development — Guia do Sistema laac"
type: system
tags: [sdd, guide, vault, agents]
created: 2026-06-07
updated: 2026-06-07
---

# Spec-Driven Development — Guia do Sistema

> "A spec é o artefato. O código é o build output. Assim como `.c` compila em binário, a spec compila em produto." — thebcms.com

---

## 1. O que é SDD neste contexto

**Spec-Driven Development** é a prática de escrever a especificação **antes** de qualquer implementação. A spec define:

- O **quê** deve ser construído (requirements)
- O **como** será construído (design)
- O **quando e por quem** (tasks)

Neste sistema, o vault Obsidian (`laac/`) é o **cérebro** — a fonte da verdade. Claude Code + os 5 agentes da SaaS Factory são os **executores**. A spec sempre vem antes do código.

**Princípio fundamental:**
Quando algo muda, a spec muda primeiro. O código é regenerado para se alinhar com ela — não o contrário.

---

## 2. Estrutura do Vault

```
laac/
├── AGENTS.md                    ← Comportamento de todos os agentes neste vault
├── INDEX.md                     ← Catálogo de todos os projetos
│
├── _system/
│   ├── SDD_GUIDE.md             ← Este documento
│   ├── AGENT_REGISTRY.md        ← Registro dos agentes da fábrica
│   └── FACTORY_PRINCIPLES.md    ← Princípios globais
│
├── Projects/
│   └── {project_id}/
│       ├── README.md            ← Entry point do projeto (o que é, links, status)
│       ├── SPEC.md              ← Constituição: problema, proposta, escopo, non-goals
│       ├── spec/
│       │   ├── requirements.md  ← REQ-001: o que o sistema DEVE fazer
│       │   ├── design.md        ← Arquitetura, modelo de dados, contratos de API
│       │   └── tasks.md         ← TASK-001: backlog atômico e rastreável
│       ├── features/
│       │   └── NNN-{feature}/
│       │       ├── spec.md      ← Spec da feature (user stories + EARS)
│       │       └── tasks.md     ← Tasks específicas da feature
│       ├── discovery/
│       │   ├── personas.md      ← ICPs e personas validadas
│       │   ├── usage-log.md     ← Observações reais de uso (feedback loop)
│       │   └── mvp-criteria.md  ← Critérios para MVP "passar"
│       ├── marketing/
│       │   ├── positioning.md   ← Posicionamento e proposta de valor
│       │   ├── brand-voice.md   ← Tom, linguagem, exemplos
│       │   └── gtm.md           ← Go-to-market por fases
│       └── decisions/
│           └── adr-NNN-*.md    ← Architecture Decision Records
│
├── Templates/
│   ├── spec-requirements.md
│   ├── spec-design.md
│   ├── spec-tasks.md
│   ├── spec-feature.md
│   ├── usage-log.md
│   ├── project-readme.md
│   └── decision.md
│
└── Scratchpad/                  ← Notas soltas, experimentos
```

**Regras de organização:**
- Tudo relacionado a um projeto vive em `Projects/{id}/` — nunca espalhado
- `PRDs/` e `Decisions/` top-level foram depreciados — o conteúdo migra para dentro do projeto
- O `SPEC.md` raiz do projeto é a **constituição** — imutável sem decisão explícita (ADR)

---

## 3. Os três documentos centrais

### `requirements.md` — O QUÊ

Usa IDs rastreáveis e notação EARS:

```markdown
## REQ-001 — Check-in diário

**Tipo:** Ubíquo
**Prioridade:** Must Have

O sistema DEVE permitir que o usuário registre produtividade (1-5),
autocuidado (1-5), gaps e notas opcionais uma vez por dia.

**Critério de aceite:**
- WHEN usuário acessa /checkin THE sistema SHALL carregar o check-in
  existente do dia, se houver
- WHEN usuário submete o formulário THE sistema SHALL fazer upsert com
  onConflict: user_id,date
- WHEN é o primeiro check-in do dia THE sistema SHALL conceder XP e
  recalcular streak
```

### `design.md` — O COMO

Documenta arquitetura, modelo de dados, contratos:

```markdown
## Arquitetura
Stack: Next.js 14 + Supabase + Vercel

## Modelo de dados
### tabela: checkins
| coluna | tipo | constraint |
|--------|------|-----------|
| user_id | uuid | FK → profiles.id |
| date | date | |
| productivity_score | int | 1-5 |
| selfcare_score | int | 1-5 |
| gaps | text[] | |
| UNIQUE(user_id, date) | | |

## Decisões técnicas
- Score calculado no client (calcDayScore em /lib/score.ts)
- Auth: email+senha via Supabase Auth (magia link depreciado por rate limit)
```

### `tasks.md` — O QUANDO

Checklist atômico, cada task referencia seu REQ:

```markdown
## Backlog

- [ ] TASK-001 [REQ-001] Implementar /checkin page com formulário
  - Input: layout da página, Supabase client
  - Output: src/app/checkin/page.tsx
  - Verificação: formulário salva e faz upsert corretamente

- [x] TASK-002 [REQ-001] Detectar check-in existente e pré-preencher form
  - Input: TASK-001 completo
  - Output: useEffect com query + setIsUpdate(true)
  - Verificação: ao acessar /checkin com check-in do dia, form vem preenchido
```

---

## 4. Notação EARS para critérios de aceite

Cinco padrões que eliminam ambiguidade para agentes:

| Padrão | Formato | Quando usar |
|--------|---------|------------|
| Ubíquo | `O sistema DEVE [comportamento]` | Regras sempre válidas |
| Event-driven | `WHEN [trigger] THE [sistema] SHALL [resposta]` | Reação a ações do usuário |
| State-driven | `WHILE [estado] THE [sistema] SHALL [comportamento]` | Comportamento em estado específico |
| Unwanted behavior | `IF [condição indesejada] THEN THE [sistema] SHALL [resposta]` | Tratamento de erro |
| Feature opcional | `WHERE [feature ativa] THE [sistema] SHALL [comportamento]` | Feature flags |

**Exemplos práticos (Flouwy):**
```
WHEN usuário adiciona primeira meta do dia THE dashboard SHALL exibir anel colorido (não neutro)
WHILE loading = true THE lista de metas SHALL exibir 3 skeleton cards
IF goals.length === 0 AND checkin === null THEN DayScore SHALL exibir anel cinza com "—"
WHEN streak chega a 7 dias THE sistema SHALL conceder badge streak_7 e notificar
```

---

## 5. Ciclo SDD — Como trabalhar

```
SPECIFY → PLAN → TASKS → IMPLEMENT → VALIDATE → (volta ao SPECIFY se mudar)
   ↑                                       |
   └───────── spec é atualizada ←──────────┘
```

### Fluxo por agente

| Fase | Agente responsável | Lê | Escreve |
|------|-------------------|-----|---------|
| SPECIFY | Product Agent | `discovery/`, `SPEC.md` | `spec/requirements.md` |
| PLAN | Product + Engineer Agent | `requirements.md` | `spec/design.md` |
| TASKS | Engineer Agent | `design.md` | `spec/tasks.md`, `features/NNN/tasks.md` |
| IMPLEMENT | Claude Code (direto) | `tasks.md`, `design.md` | código |
| VALIDATE | QA Agent | `requirements.md`, código | relatório de gaps |
| MARKET | Marketing Agent | `SPEC.md`, `discovery/` | `marketing/*.md` |
| DECIDE | Manager Agent | tudo | `decisions/adr-NNN.md` |

### Regra de atualização

> Nunca atualize o código sem atualizar a spec. Se uma tarefa revelou uma decisão de design, ela vai para `design.md`. Se um requisito mudou, ele vai para `requirements.md` com a data da mudança.

---

## 6. Integração com Claude Code

### CLAUDE.md no repositório

Cada repo de código deve ter um `CLAUDE.md` que aponta para o vault:

```markdown
# CLAUDE.md — Flouwy

## Spec
Este projeto segue Spec-Driven Development.
Spec master: C:/Users/MarcusMoraes/Documents/laac/Projects/flouwy/SPEC.md
Requirements: .../spec/requirements.md
Design: .../spec/design.md
Tasks: .../spec/tasks.md

## Boundaries
✅ Sempre: editar arquivos em src/, rodar tsc --noEmit
⚠️ Perguntar primeiro: mudar schema do banco, alterar middleware, alterar lógica de score
🚫 Nunca: commitar segredos, fazer push sem confirmação, alterar migrations aplicadas
```

### Como os agentes leem o vault

O `chat_manager.py` carrega contexto do vault automaticamente. Com a nova estrutura, ele deve ler:
1. `AGENTS.md` — regras gerais
2. `Projects/{id}/SPEC.md` — constituição do projeto
3. `Projects/{id}/spec/requirements.md` — requisitos ativos
4. `Projects/{id}/discovery/` — contexto de usuário

---

## 7. MCPs e Skills recomendados

### Para instalar

```bash
# Obsidian Skills (oficial — Steph Ango, CEO do Obsidian)
# Permite Claude Code ler/escrever no vault nativamente
# https://github.com/kepano/obsidian-skills

# cc-sdd — Spec workflow completo para Claude Code
npx cc-sdd install --claude-skills
# Adiciona skills: /specify, /plan, /tasks, /implement
```

### Skills úteis
- `cc-sdd` — workflows `/specify`, `/plan`, `/tasks`, `/implement` direto no Claude Code
- `kepano/obsidian-skills` — Claude Code lê e escreve no vault sem scripts manuais
- `FredAntB/Spec-Driven-Development` — gera `requirements.md`, `design.md`, `tasks.md` automaticamente

---

## 8. Anti-padrões a evitar

| Anti-padrão | Problema | Solução |
|-------------|----------|---------|
| Spec vaga ("o sistema deve ser rápido") | Agente não sabe o que validar | Use EARS com métricas mensuráveis |
| Spec gigante sem hierarquia | Desempenho do agente cai com specs longas | Quebre em features/NNN/ |
| Código sem spec correspondente | Próximo agente não tem contexto | Escreva spec retroativa antes de continuar |
| Spec nunca atualizada | Fica desalinhada com o código | Regra: code review inclui spec review |
| Copiar spec inteira em todo contexto | Tokens desperdiçados | Passe apenas a seção relevante por task |

---

## 9. Commits rastreáveis

Formato para commits que referenciam specs:

```
feat(checkin): detectar check-in existente e mostrar modo atualizar

refs specs/001-checkin/spec.md REQ-001
TASK-002 ✅
```

---

## Referências

- [Thoughtworks — Spec-Driven Development 2025](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices)
- [Addy Osmani — How to write a good spec for AI agents](https://addyosmani.com/blog/good-spec/)
- [BCMS — SDD Definitive Guide 2026](https://thebcms.com/blog/spec-driven-development)
- [cc-sdd — Claude Code SDD Skills](https://github.com/gotalab/cc-sdd)
- [MindStudio — AI-Intelligent Obsidian Vault Architecture](https://www.mindstudio.ai/blog/ai-second-brain-obsidian-vault-folder-architecture)
