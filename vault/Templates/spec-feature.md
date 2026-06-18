---
title: "Template — features/NNN-{slug}/spec.md"
type: template
---

# Feature Spec: {nome da feature}

**ID:** features/NNN-{slug}
**Status:** Draft | Em revisão | Aprovado | Implementado
**Agente que aprovou:** Product Agent
**Data:** YYYY-MM-DD

---

## Problema que resolve

{Uma ou duas frases. Qual dor do usuário essa feature alivia?}

Referência persona: [[discovery/personas]] — {nome da persona}

---

## User Stories

```
Como {tipo de usuário}
Quero {ação ou capacidade}
Para {benefício ou objetivo}
```

**Story 1:**
```
Como usuário com TDAH
Quero ver meu score do dia como anel visual colorido
Para ter clareza imediata sobre meu progresso sem processar números
```

---

## Comportamento esperado (EARS)

```
WHEN {trigger}
  THE {sistema} SHALL {comportamento}

WHILE {estado}
  THE {sistema} SHALL {comportamento}

IF {erro ou edge case}
  THEN THE {sistema} SHALL {tratamento}
```

---

## Out-of-scope explícito

- {O que esta feature NÃO inclui — tão importante quanto o que inclui}
- {Ex: Não inclui notificação push — isso é feature separada REQ-XXX}

---

## Design notes

{Links para seções relevantes em spec/design.md}

- Componente: `src/components/...`
- Página: `src/app/...`
- Banco: tabela `{nome}`, coluna `{nome}`

---

## Critérios de aceite finais

- [ ] {Critério testável 1}
- [ ] {Critério testável 2}
- [ ] {Critério testável 3}

---

## Tasks derivadas

Ver: [[spec/tasks.md]] — TASK-{NNN} a TASK-{NNN}
