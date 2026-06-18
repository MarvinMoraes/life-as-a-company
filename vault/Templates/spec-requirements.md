---
title: "Template — spec/requirements.md"
type: template
---

# Requirements — {project_id}

> Fonte da verdade sobre O QUÊ o sistema deve fazer.
> Usa notação EARS. Nunca edite sem atualizar a data.
> Última atualização: YYYY-MM-DD

---

## REQ-001 — {nome do requisito}

**Tipo:** Must Have | Should Have | Could Have
**Agente responsável:** Product
**Status:** Draft | Aprovado | Implementado | Depreciado

### Descrição
{Uma frase clara sobre o comportamento esperado}

### Critérios de aceite (EARS)
```
WHEN [trigger/ação do usuário]
  THE [sistema/componente] SHALL [resposta esperada]

WHILE [estado em que o sistema está]
  THE [sistema] SHALL [comportamento contínuo]

IF [condição de erro ou edge case]
  THEN THE [sistema] SHALL [tratamento]
```

### Out-of-scope
- {O que explicitamente NÃO está incluído neste requisito}

### Notas
- Referência: [[decisions/adr-NNN]]
- Implementado em: `src/...`

---

## REQ-002 — {próximo requisito}

...

---

## Changelog

| Data | Requisito | Mudança | Motivo |
|------|-----------|---------|--------|
| YYYY-MM-DD | REQ-001 | Criado | Discovery inicial |
