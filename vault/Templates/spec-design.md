---
title: "Template — spec/design.md"
type: template
---

# Design — {project_id}

> Fonte da verdade sobre O COMO o sistema é construído.
> Arquitetura, modelo de dados, contratos de API, decisões técnicas.
> Última atualização: YYYY-MM-DD

---

## Stack

| Camada | Tecnologia | Versão | Decisão |
|--------|-----------|--------|---------|
| Frontend | | | |
| Backend/BaaS | | | |
| Deploy | | | |
| Auth | | | |

Ver: [[decisions/adr-NNN-stack]]

---

## Arquitetura geral

```
[diagrama ou descrição do fluxo principal]

Ex:
Browser → Next.js App Router → Supabase (Auth + DB + RLS)
                             ↑
                        middleware.ts (session refresh)
```

---

## Modelo de dados

### Tabela: {nome}

| Coluna | Tipo | Constraint | Descrição |
|--------|------|-----------|-----------|
| id | uuid | PK, default gen_random_uuid() | |
| user_id | uuid | FK → profiles.id | |
| created_at | timestamptz | default now() | |

**RLS:** {descrever política de row-level security}

---

## Contratos de API / Funções principais

### `{nomeDoArquivo}.ts` — `{nomeDaFunção}`

```typescript
// Assinatura
function nomeDaFunção(params: TipoParam): TipoRetorno

// Comportamento
// - Descreva o que faz
// - Descreva edge cases tratados
```

---

## Decisões técnicas registradas

| Decisão | Escolha | Alternativa descartada | Motivo |
|---------|---------|----------------------|--------|
| Auth method | email+senha | magic link | rate limit Supabase (3/hora) |

---

## Constraints conhecidas

- {Ex: Supabase free tier: 500MB storage, 2 projects}
- {Ex: Vercel hobby: sem cron jobs}

---

## Changelog

| Data | Seção | Mudança | Refs |
|------|-------|---------|------|
| YYYY-MM-DD | | Criado | |
