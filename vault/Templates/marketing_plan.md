---
title: "Marketing Plan: {{ project_id }}"
type: marketing
project_id: {{ project_id }}
tags:
  - marketing
  - gtm
  - {{ project_id }}
summary: "GTM: {{ positioning_statement[:120] }}"
created: {{ now.strftime('%Y-%m-%d') }}
---

# Marketing Plan: {{ project_id }}

## Mercado
**Tamanho:** {{ market_size }}
**Segmento-alvo:** {{ target_segment }}

## Posicionamento
{{ positioning_statement }}

**UVP:** {{ unique_value_proposition }}

## Concorrência

{% for competitor in competitors %}
### {{ competitor.name }}
- **Forças:** {{ competitor.strengths | join(', ') }}
- **Fraquezas:** {{ competitor.weaknesses | join(', ') }}
- **Posicionamento:** {{ competitor.positioning }}
{% endfor %}

## Mensagens por Canal
{% for channel, message in messaging.items() %}
**{{ channel }}:** {{ message }}
{% endfor %}

## Canais de Aquisição

{% for channel in acquisition_channels %}
### {{ channel.channel }} — Prioridade: {{ channel.priority | upper }}
**Hipótese:** {{ channel.hypothesis }}
**CAC Estimado:** {{ channel.estimated_cac }}
{% endfor %}

## Estratégia Go-to-Market
{{ gtm_strategy }}

## Fases de Lançamento

{% for phase in launch_phases %}
### Fase {{ phase.phase }}: {{ phase.name }}
{% for action in phase.actions %}
- {{ action }}
{% endfor %}
**Métrica de sucesso:** {{ phase.success_metric | default('A definir') }}
{% endfor %}

## KPIs
{% for kpi in kpis %}
- {{ kpi }}
{% endfor %}

---
*Gerado pela SaaS Factory — Marketing & Ads Strategist Agent*
