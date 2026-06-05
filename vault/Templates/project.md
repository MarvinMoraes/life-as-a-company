---
title: {{ title }}
type: project
project_id: {{ project_id }}
tags:
  - project
  - {{ project_id }}
summary: {{ summary }}
created: {{ now.strftime('%Y-%m-%d') }}
updated: {{ now.strftime('%Y-%m-%d') }}
status: {{ status | default('ideation') }}
---

# {{ title }}

## Visão Geral
{{ vision | default('A definir.') }}

## Problema
{{ problem | default('A definir.') }}

## Proposta de Valor
{{ value_proposition | default('A definir.') }}

## Status Atual
**Fase:** {{ status | default('ideation') }}
**Versão do PRD:** {{ prd_version | default('—') }}
**Última atualização:** {{ now.strftime('%Y-%m-%d') }}

## Links Relacionados
- [[{{ project_id }}-prd-v1]] — PRD
- [[{{ project_id }}-marketing-plan]] — Plano de Marketing
- [[{{ project_id }}-adr-001]] — Primeira Decisão

## Notas
<!-- Adicione contexto adicional aqui -->
