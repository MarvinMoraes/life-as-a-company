---
title: "PRD: {{ title }} v{{ version | default('1.0') }}"
type: prd
project_id: {{ project_id }}
tags:
  - prd
  - {{ project_id }}
summary: "PRD v{{ version | default('1.0') }}: {{ executive_summary[:120] }}"
created: {{ now.strftime('%Y-%m-%d') }}
version: "{{ version | default('1.0') }}"
approved: {{ approved | default(false) }}
---

# PRD: {{ title }}

**Versão:** {{ version | default('1.0') }}
**Status:** {{ 'Aprovado ✓' if approved else 'Em Revisão' }}
**Data:** {{ now.strftime('%Y-%m-%d') }}

## Resumo Executivo
{{ executive_summary }}

## Problema
{{ problem }}

## Solução
{{ solution }}

## Personas

{% for persona in personas %}
### {{ persona.name }} ({{ persona.role }})
**Job-to-be-Done:** {{ persona.jtbd }}

**Dores:**
{% for pain in persona.pains %}
- {{ pain }}
{% endfor %}
{% endfor %}

## Proposta de Valor
{{ value_proposition }}

## Features

{% for feature in features %}
### {{ feature.name }} — `{{ feature.priority | upper }}`
{{ feature.description }}

**Critérios de Aceite:**
{% for ac in feature.acceptance_criteria %}
- [ ] {{ ac }}
{% endfor %}
{% endfor %}

## Fora do Escopo
{% for item in out_of_scope %}
- {{ item }}
{% endfor %}

## Métricas de Sucesso
{% for metric in success_metrics %}
- {{ metric }}
{% endfor %}

## Roadmap

{% for phase in roadmap_phases %}
### Fase {{ phase.phase }}: {{ phase.name }}
**Duração estimada:** {{ phase.duration | default('A definir') }}
Features: {{ phase.features | join(', ') }}
{% endfor %}

## Riscos
{% for risk in risks %}
- {{ risk }}
{% endfor %}

---
*Gerado pela SaaS Factory — Product Strategist Agent*
