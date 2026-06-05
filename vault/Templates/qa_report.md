---
title: "QA Report: {{ artifact_evaluated }}"
type: qa
project_id: {{ project_id }}
tags:
  - qa
  - {{ project_id }}
summary: "QA: {{ verdict }} (score {{ score }}) — {{ summary[:100] }}"
created: {{ now.strftime('%Y-%m-%d') }}
verdict: {{ verdict }}
score: {{ score }}
---

# QA Report: {{ artifact_evaluated }}

**Projeto:** {{ project_id }}
**Veredicto:** {{ verdict | upper }}
**Score:** {{ score }}/10
**Data:** {{ now.strftime('%Y-%m-%d') }}

## Resumo
{{ summary }}

{% if prd_adherence %}
## Aderência ao PRD
{{ prd_adherence }}%
{% endif %}

## Achados

{% for finding in findings %}
### [{{ finding.severity | upper }}] {{ finding.category }}
**Descrição:** {{ finding.description }}
**Recomendação:** {{ finding.recommendation }}

{% endfor %}

{% if missing_acceptance_criteria %}
## Critérios de Aceite Faltantes
{% for ac in missing_acceptance_criteria %}
- [ ] {{ ac }}
{% endfor %}
{% endif %}

---
*Gerado pela SaaS Factory — QA Agent*
