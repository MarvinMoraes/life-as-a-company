# INDEX — Vault laac

> Catálogo de todos os projetos e documentos do sistema.
> Agentes leem este arquivo para entender o que existe antes de buscar arquivos específicos.
> Atualizado: 2026-06-17

---

## Sistema

| Arquivo | Descrição |
|---------|-----------|
| [[AGENTS]] | Comportamento de todos os agentes neste vault |
| [[_system/MARCUS]] | Perfil do usuário — quem é Marcus, regras de comunicacao, preferências |
| [[_system/SDD_GUIDE]] | Guia completo de Spec-Driven Development |
| [[_system/AGENT_REGISTRY]] | Registro dos agentes da SaaS Factory |
| [[_system/FACTORY_PRINCIPLES]] | Princípios globais da fábrica |

---

## Projetos ativos

### Flouwy (`Projects/flouwy/`)

App de performance para neurodivergentes. MVP em progresso.
Stack: Next.js 14 + Supabase. Status: polish + deploy pendente.

| Arquivo | Conteúdo |
|---------|----------|
| `SPEC.md` | Constituição: problema, proposta, escopo, non-goals |
| `spec/requirements.md` | REQ-001 a REQ-006 — o que o sistema deve fazer |
| `spec/design.md` | Arquitetura, modelo de dados, funções-chave, decisões técnicas |
| `spec/tasks.md` | Backlog atômico — TASK-001 a TASK-022 |
| `discovery/personas.md` | ICPs e personas |
| `discovery/usage-log.md` | Observações reais de uso (feedback loop) |
| `discovery/mvp-criteria.md` | Quando o MVP "passou" |
| `marketing/positioning.md` | Posicionamento e proposta de valor |
| `marketing/brand-voice.md` | Tom, linguagem, exemplos de copy |
| `marketing/gtm.md` | Go-to-market por fases |
| `decisions/adr-001-*.md` | Decisão: nome Flouwy e posicionamento |
| `features/001-checkin/spec.md` | Feature: check-in diário |
| `features/002-habits/spec.md` | Feature: hábitos recorrentes |
| `features/003-gamification/spec.md` | Feature: gamificação sem pressão |
| `features/004-score/spec.md` | Feature: score do dia |

### YouTube Kids Factory (`Projects/youtube-agent/`)

Pipeline automatizado de criação e publicação de vídeos infantis no YouTube.
Stack: Python 3.11, Claude, Suno AI, ElevenLabs, InVideo AI, YouTube Data API, n8n.
Co-proprietários: Marcus Moraes + Willian Silva.

| Arquivo | Conteúdo |
|---------|----------|
| `SPEC.md` | Constituição: problema, proposta, escopo, non-goals |
| `spec/requirements.md` | REQ-001 a REQ-006 — pipeline dos 5 agentes |
| `spec/design.md` | Arquitetura, LLM router, integrações, decisões |
| `spec/tasks.md` | Backlog de melhorias |
| `discovery/channels.md` | Estratégia pt-infantil e en-kids |

---

## Templates disponíveis

| Template | Para usar quando |
|----------|-----------------|
| `Templates/spec-requirements.md` | Criar requirements.md de projeto novo |
| `Templates/spec-design.md` | Criar design.md de projeto novo |
| `Templates/spec-tasks.md` | Criar tasks.md de projeto novo |
| `Templates/spec-feature.md` | Documentar nova feature (features/NNN-slug/) |
| `Templates/usage-log.md` | Iniciar feedback loop de projeto novo |
| `Templates/decision.md` | Criar ADR |

---

## Scratchpad

Notas soltas em `Scratchpad/`. Não fazem parte de nenhum projeto formal.
