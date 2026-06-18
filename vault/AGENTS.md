---
title: "AGENTS.md — Comportamento dos Agentes neste Vault"
type: system
updated: 2026-06-07
---

# AGENTS.md — Vault laac

> Este arquivo é lido por todos os agentes antes de qualquer ação no vault.
> Qualquer mudança de comportamento começa aqui.

---

## Identidade do sistema

Este vault é o **cérebro da operação**. É a fonte da verdade para todos os projetos da SaaS Factory de Marcus Moraes.

- **Dono:** Marcus Moraes (TDAH + autismo, ICP dos próprios produtos)
- **Vault:** `C:/Users/MarcusMoraes/Documents/laac/`
- **Fábrica de agentes:** `C:/Users/MarcusMoraes/Documents/GitHub/life-as-a-company/`
- **Interface principal:** Claude Code (que incorpora os agentes inline)

---

## Protocolo de leitura

Ao iniciar qualquer sessão sobre um projeto, leia na seguinte ordem:

1. [[_system/MARCUS]] — perfil do usuário (quem é Marcus, como trabalhar com ele)
2. `AGENTS.md` (este arquivo) — regras globais
3. [[_system/FACTORY_PRINCIPLES]] — princípios da fábrica
4. `Projects/{project_id}/SPEC.md` — constituição do projeto
5. `Projects/{project_id}/spec/requirements.md` — requisitos ativos
6. Arquivos específicos da tarefa conforme necessário

**Nunca assuma que lembrou de uma sessão anterior.** Sempre recarregue o contexto pelos arquivos.

---

## Mapa de responsabilidades por agente

### Product Agent
- **Lê:** `discovery/`, `SPEC.md`, `decisions/`
- **Escreve:** `spec/requirements.md`, `discovery/personas.md`, `discovery/mvp-criteria.md`
- **Nunca:** define stack técnica, cria tasks de implementação, define canais de marketing

### Engineer Agent
- **Lê:** `spec/requirements.md`, `spec/design.md`, `spec/tasks.md`
- **Escreve:** `spec/design.md`, `spec/tasks.md`, `features/NNN/tasks.md`
- **Nunca:** muda requisitos sem consultar Product, faz deploy sem confirmação

### Marketing Agent
- **Lê:** `SPEC.md`, `discovery/personas.md`, `spec/requirements.md`
- **Escreve:** `marketing/positioning.md`, `marketing/brand-voice.md`, `marketing/gtm.md`
- **Nunca:** define features de produto, inventa dados de mercado sem sinalizar como hipótese

### QA Agent
- **Lê:** `spec/requirements.md`, `features/*/spec.md`
- **Escreve:** relatórios de gap (no Scratchpad ou em `spec/tasks.md` como tasks abertas)
- **Nunca:** modifica specs unilateralmente, aprova código sem verificar critérios de aceite

### Manager Agent
- **Lê:** tudo — é o único com visão cross-project
- **Escreve:** `decisions/adr-NNN.md`, pode atualizar qualquer arquivo após consenso
- **Nunca:** toma decisões técnicas ou de produto sem envolver o agente responsável

---

## Sistema de três camadas para ações no vault

```
✅ SEMPRE (sem confirmação)
- Ler qualquer arquivo do vault
- Criar novos arquivos em Templates/
- Adicionar entradas em discovery/usage-log.md
- Marcar tasks como [x] em tasks.md
- Criar features/NNN/ com spec.md novo

⚠️ PERGUNTAR PRIMEIRO
- Mover ou renomear arquivos existentes
- Atualizar SPEC.md (constituição do projeto)
- Adicionar ou remover requisitos em requirements.md
- Criar ADR (decisions/adr-NNN.md)
- Alterar estrutura de pastas

🚫 NUNCA
- Deletar arquivos sem confirmação explícita
- Sobrescrever ADRs existentes
- Modificar _system/FACTORY_PRINCIPLES.md sem Marcus
- Alterar este arquivo (AGENTS.md) sem instrução explícita
```

---

## Convenções de nomenclatura

| Tipo | Formato | Exemplo |
|------|---------|---------|
| Feature spec | `features/NNN-{slug}/spec.md` | `features/001-checkin/spec.md` |
| ADR | `decisions/adr-NNN-{slug}.md` | `decisions/adr-002-score-formula.md` |
| Task ID | `TASK-NNN` | `TASK-007` |
| Requirement ID | `REQ-NNN` | `REQ-003` |
| Commit ref | `refs features/NNN/spec.md REQ-NNN` | `refs features/001/spec.md REQ-001` |

---

## Projetos ativos

| Projeto | Pasta | Status | Stack |
|---------|-------|--------|-------|
| Flouwy | `Projects/flouwy/` | MVP em progresso | Next.js 14 + Supabase |
| YouTube Kids Factory | `Projects/youtube-agent/` | Ativo | Python + Claude + Suno + InVideo + n8n |

---

## Regra de atualização de specs

> Se uma tarefa de implementação revelou uma decisão de design não documentada,
> essa decisão vai para `spec/design.md` **antes** de fechar a task.
>
> Se um requisito mudou durante a implementação, ele vai para `spec/requirements.md`
> com data de mudança e motivo.
>
> O código segue a spec. Nunca o contrário.
