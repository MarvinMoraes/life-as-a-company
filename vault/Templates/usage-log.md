---
title: "Template — discovery/usage-log.md"
type: template
---

# Usage Log — {project_id}

> Observações reais de uso. Este é o feedback loop que alimenta o Product Agent.
> Formato livre — anote o que percebeu, não o que acha que deveria perceber.
> Entrada mínima: data + o que aconteceu.

---

## Como usar

1. Após usar o app, reserve 2 minutos para anotar
2. Não filtre — insights negativos são mais valiosos
3. Classifique com tag: `[bug]`, `[ux]`, `[missing]`, `[works]`, `[habit]`
4. O Product Agent lê este arquivo para fechar open questions do PRD

---

## Entradas

### YYYY-MM-DD

**Sessão:** {manhã/tarde/noite}
**Tags:** [ux] [missing] [works]

{Observação livre. O que aconteceu? O que sentiu? O que faltou?}

**Insight acionável:** {Se tiver — o que deveria mudar?}
**Refs:** REQ-{NNN} | features/{NNN}

---

### YYYY-MM-DD

...

---

## Padrões identificados (atualizado pelo Product Agent)

| Padrão | Frequência | Refs | Status |
|--------|-----------|------|--------|
| {Ex: Não faz check-in quando cansado} | 3x | REQ-003 | Open question |
| {Ex: Hábitos auto-populate muito lento} | 2x | TASK-012 | Corrigido |

---

## Open questions fechadas por este log

- [ ] OQ-001: Usuário faz check-in por 7 dias seguidos? → {evidência}
- [ ] OQ-002: Tempo médio de check-in ≤ 2 minutos? → {evidência}
