---
title: "Template — spec/tasks.md"
type: template
---

# Tasks — {project_id}

> Backlog atômico e rastreável. Cada task é independente e verificável.
> Formato: [ ] TASK-NNN [REQ-NNN] Descrição
> Última atualização: YYYY-MM-DD

---

## Legenda

```
[ ]  = pendente
[x]  = concluída
[~]  = em andamento
[!]  = bloqueada (ver nota)
```

---

## Fase atual: {nome da fase — ex: MVP, Phase 2}

### {Área ou feature}

- [ ] TASK-001 [REQ-001] {Descrição da task}
  - **Input:** {arquivos ou contexto necessário}
  - **Output:** {arquivo criado/modificado}
  - **Verificação:** {como confirmar que está correto}
  - **Agente:** Claude Code | Engineer Agent

- [x] TASK-002 [REQ-001] {Task já concluída}
  - **Concluída em:** YYYY-MM-DD
  - **Refs:** commit {hash} | PR #{n}

- [!] TASK-003 [REQ-002] {Task bloqueada}
  - **Bloqueada por:** TASK-001 pendente
  - **Nota:** {contexto do bloqueio}

---

## Backlog futuro (Phase 2+)

- [ ] TASK-050 [REQ-XXX] {Feature futura}

---

## Implementation Notes

> Aprendizados que afetam tasks subsequentes. Agentes leem esta seção antes de executar.

- {Ex: A query de checkins precisa de .single() pois o constraint user_id,date é único}
- {Ex: O score deve ser recalculado no client, não no banco, para evitar computed columns}

---

## Changelog

| Data | Task | Mudança |
|------|------|---------|
| YYYY-MM-DD | TASK-001 | Criado |
