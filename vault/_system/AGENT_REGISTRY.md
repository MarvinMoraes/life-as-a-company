---
title: Agent Registry
type: system
version: "2.0"
updated: 2026-06-17
tags:
  - system
  - agents
---

# Agent Registry

Registro dos 5 agentes da fábrica com políticas de uso e capacidades de Fase 2.

## Manager / Orchestrator
- **Quando usar:** sempre — é o ponto de entrada de qualquer interação
- **Quando NÃO usar:** nunca invoque outros agentes diretamente, sempre via Manager
- **Token budget:** 2.048 (planejamento) / 1.024 (consolidação)
- **Tools nativas:** `delegate_to_agent`, `read_file` (vault), `write_file` (vault)
- **MCPs:** `github_list_issues`, `github_create_pull_request`
- **Memória:** escreve DecisionRecords e ExecutionSnapshots
- **Notas:** agent_caller é uma closure sem import circular — Manager pode invocar outros agentes dentro do loop agêntico

## Product Strategist
- **Quando usar:** discovery, definição de escopo, criação/atualização de PRD
- **Quando NÃO usar:** após PRD aprovado sem necessidade de mudança
- **Token budget:** 4.096 (PRD completo) / 1.024 (atualização)
- **Tools nativas:** `read_file` (vault + flouwy docs), `write_file` (vault)
- **MCPs:** `web_search` (pesquisa de mercado, análise de concorrentes)
- **Memória:** escreve PRDs e notas de Research

## Senior Full Stack Engineer
- **Quando usar:** após PRD aprovado — arquitetura, código, revisão técnica, implementação real
- **Quando NÃO usar:** antes de PRD aprovado pelo QA
- **Token budget:** 4.096 (implementação deep) / 1.536 (revisão)
- **Tools nativas:** `list_files`, `read_file`, `write_file` (flouwy), `run_command` (npm run dev)
- **MCPs:** `github_create_pull_request`, `github_search_code`, `git_diff`, `git_status`
- **Memória:** escreve TechnicalPlans e ADRs técnicos
- **Root path:** flouwy (`C:/Users/MarcusMoraes/Documents/GitHub/flowly`)

## Marketing & Ads Strategist
- **Quando usar:** posicionamento, GTM, análise de mercado, campanhas
- **Quando NÃO usar:** antes de personas e proposta de valor definidos
- **Token budget:** 2.048 (plano completo) / 512 (análise pontual)
- **Tools nativas:** `read_file` (vault), `write_file` (vault)
- **MCPs:** `web_search` (pesquisa competitiva, tendências)
- **Memória:** escreve MarketingPlans e notas de Research competitivo

## Quality Assurance
- **Quando usar:** após qualquer entrega relevante de outro agente; obrigatório antes de aprovar código
- **Quando NÃO usar:** para revisão de rascunhos intermediários
- **Token budget:** 2.048 (auditoria) / 1.024 (revisão padrão)
- **Tools nativas:** `read_file` (flouwy, read-only), `run_command` (npm run lint, npm run build)
- **MCPs:** nenhum
- **Memória:** escreve QA Reports
- **Root path:** flouwy (read only — sem escrita)

---

## Comandos Permitidos (allowlist run_command)

```python
ALLOWED_COMMANDS = {
    "npm run build": ["npm", "run", "build"],
    "npm run lint":  ["npm", "run", "lint"],
    "npm run dev":   ["npm", "run", "dev"],
}
```

Timeout: 120s. Output: truncado em 3000 chars. Sem `shell=True`.
