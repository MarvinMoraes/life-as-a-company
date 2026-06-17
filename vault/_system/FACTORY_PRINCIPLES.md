---
title: Factory Principles
type: system
version: "2.0"
updated: 2026-06-17
tags:
  - system
  - principles
---

# SaaS Factory — Princípios Fundamentais

## Missão
Operar como uma fábrica de SaaS pessoal, capaz de levar uma ideia até um produto funcional com disciplina de contexto, memória estruturada e execução real — agentes que lêem código, escrevem arquivos e rodam comandos.

## Os 5 Agentes

| Agente | Responsabilidade Central | Tools Disponíveis |
|--------|--------------------------|-------------------|
| Manager | Orquestra, delega, controla contexto | `delegate_to_agent`, `read_file` (vault), `write_file` (vault), GitHub MCP |
| Product Strategist | Discovery, PRD, personas, roadmap | `read_file` (vault+docs), `write_file` (vault), `web_search` |
| Senior Engineer | Arquitetura, stack, implementação de código | `read_file`, `write_file`, `list_files` (flouwy), GitHub MCP |
| Marketing Strategist | Mercado, posicionamento, canais, GTM | `read_file` (vault), `write_file` (vault), `web_search` |
| QA | Revisão, veredictos, lint e build | `read_file` (flouwy), `run_command` (lint/build) |

## Princípios de Operação

### 1. Responsabilidade Única
Cada agente tem um papel e não deve sair dele.
O Manager não coda. O Engineer não define posicionamento. O QA não propõe soluções.

### 2. Contexto como Recurso Escasso
Tokens são caros. O Manager monta context packs mínimos.
Agentes recebem apenas o que precisam para a tarefa atual.
Histórico completo nunca é carregado — apenas resumos e notas relevantes.
Prompt caching (`cache_control: ephemeral`) em system prompts ≥ 1024 tokens para ~90% de custo em cache hits.

### 3. Memória como Primeira Busca
Antes de gerar algo novo, verificar o vault.
Se já existe uma decisão ou análise, recuperar — não recriar.

### 4. Decisões Explícitas
Toda decisão importante (técnica, de produto, estratégica) vira um ADR no vault.
Decisões implícitas viram dívidas futuras.

### 5. QA é Obrigatório
Nenhum artefato passa sem revisão do QA Agent.
Para código: QA executa `npm run lint` e `npm run build` com tools reais.
Um score abaixo de 7.0 gera loop de revisão.

### 6. Out-of-scope é Produto
Saber o que NÃO fazer é tão valioso quanto saber o que fazer.
O Product Agent é responsável por manter o out-of-scope atualizado.

### 7. Execução Real, Não Apenas Planejamento
Agentes com `tool_executor` podem ler e escrever arquivos reais, rodar comandos e delegar uns aos outros.
O loop agêntico (LLM → tool call → resultado → LLM) roda até `end_turn` ou 10 iterações.

## Camadas de Tool Use

```
Nativas (Anthropic function calling)
  read_file       → lê arquivo dentro do root permitido
  write_file      → escreve arquivo dentro do root permitido
  list_files      → lista diretório dentro do root permitido
  run_command     → executa comando da allowlist (npm run lint/build/dev)
  delegate_to_agent → Manager delega para outro agente via closure

MCPs (subprocesso stdio, graceful degradation)
  github          → github_list_issues, github_create_pull_request, github_search_code
  brave-search    → web_search (pesquisa de mercado, concorrentes)
  sequential-thinking → raciocínio estruturado em múltiplos passos
  memory          → create_entities, search_nodes, add_observations
  git             → git_diff, git_log, git_status, git_blame
```

## Segurança de Paths

Cada role tem um root permitido. `ToolExecutor._resolve_safe()` usa `Path.resolve()` para bloquear `../` traversal:

| Role | Read roots | Write roots |
|------|-----------|-------------|
| Manager | vault | vault |
| Engineer | flouwy | flouwy |
| Product | vault + flouwy | vault |
| Marketing | vault | vault |
| QA | flouwy | — (read only) |

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
