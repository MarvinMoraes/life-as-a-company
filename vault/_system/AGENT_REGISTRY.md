---
title: Agent Registry
type: system
tags:
  - system
  - agents
---

# Agent Registry

Registro dos 5 agentes da fábrica com suas políticas de uso.

## Manager / Orchestrator
- **Quando usar:** sempre — é o ponto de entrada de qualquer interação
- **Quando NÃO usar:** nunca invoque outros agentes diretamente, sempre via Manager
- **Token budget:** 2.048 (planejamento) / 1.024 (consolidação)
- **Memória:** escreve DecisionRecords e ExecutionSnapshots

## Product Strategist
- **Quando usar:** discovery, definição de escopo, criação/atualização de PRD
- **Quando NÃO usar:** após PRD aprovado sem necessidade de mudança
- **Token budget:** 4.096 (PRD completo) / 1.024 (atualização)
- **Memória:** escreve PRDs e notas de Research

## Senior Full Stack Engineer
- **Quando usar:** após PRD aprovado — arquitetura, código, revisão técnica
- **Quando NÃO usar:** antes de PRD aprovado pelo QA
- **Token budget:** 3.072 (arquitetura) / 1.536 (revisão)
- **Memória:** escreve TechnicalPlans e ADRs técnicos

## Marketing & Ads Strategist
- **Quando usar:** posicionamento, GTM, análise de mercado, campanhas
- **Quando NÃO usar:** antes de personas e proposta de valor definidos
- **Token budget:** 2.048 (plano completo) / 512 (análise pontual)
- **Memória:** escreve MarketingPlans e notas de Research competitivo

## Quality Assurance
- **Quando usar:** após qualquer entrega relevante de outro agente
- **Quando NÃO usar:** para revisão de rascunhos intermediários
- **Token budget:** 2.048 (auditoria) / 1.024 (revisão padrão)
- **Memória:** escreve QA Reports
