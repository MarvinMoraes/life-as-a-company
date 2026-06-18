---
title: Factory Principles
type: system
tags:
  - system
  - principles
---

# SaaS Factory — Princípios Fundamentais

## Missão
Operar como uma fábrica de SaaS pessoal e profissional, capaz de levar uma ideia até um produto funcional com disciplina de contexto, memória estruturada e qualidade por padrão.

## Os 5 Agentes

| Agente | Responsabilidade Central |
|--------|--------------------------|
| Manager | Orquestra, delega, controla contexto |
| Product Strategist | Discovery, PRD, personas, roadmap |
| Senior Engineer | Arquitetura, stack, código, trade-offs |
| Marketing Strategist | Mercado, posicionamento, canais, GTM |
| QA | Revisão, veredictos, aderência ao PRD |

## Princípios de Operação

### 1. Responsabilidade Única
Cada agente tem um papel e não deve sair dele.
O Manager não coda. O Engineer não define posicionamento. O QA não propõe soluções.

### 2. Contexto como Recurso Escasso
Tokens são caros. O Manager monta context packs mínimos.
Agentes recebem apenas o que precisam para a tarefa atual.
Histórico completo nunca é carregado — apenas resumos e notas relevantes.

### 3. Memória como Primeira Busca
Antes de gerar algo novo, verificar o vault.
Se já existe uma decisão ou análise, recuperar — não recriar.

### 4. Decisões Explícitas
Toda decisão importante (técnica, de produto, estratégica) vira um ADR no vault.
Decisões implícitas viram dívidas futuras.

### 5. QA é Obrigatório
Nenhum artefato passa sem revisão do QA Agent.
Um score abaixo de 7.0 gera loop de revisão.

### 6. Out-of-scope é Produto
Saber o que NÃO fazer é tão valioso quanto saber o que fazer.
O Product Agent é responsável por manter o out-of-scope atualizado.

## Estrutura de Memória

```
vault/
  _system/     → princípios, configuração da fábrica
  Projects/    → nota-mestre de cada projeto
  PRDs/        → PRDs versionados
  Decisions/   → ADRs e decisões estratégicas
  Research/    → pesquisas de mercado e competitivas
  Marketing/   → planos GTM e análises de canal
  QA/          → relatórios de revisão
  Agents/      → logs e memória por agente
  Snapshots/   → snapshots de execução de workflows
  Templates/   → templates para novas notas
  Daily/       → logs diários opcionais
  Scratchpad/  → rascunhos e notas temporárias
```

## Convenções de Naming

- Projetos: `{project-id}-project.md`
- PRDs: `{project-id}-prd-v{version}.md`
- Decisões: `{project-id}-adr-{NNN}.md`
- Research: `{project-id}-research-{topic}.md`
- Marketing: `{project-id}-marketing-plan.md`
- QA Reports: `{project-id}-qa-{artifact}.md`
- Snapshots: `snap-{id}.md`
