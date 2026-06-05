---
title: {{ decision_id }}: {{ title }}
type: decision
project_id: {{ project_id | default('~') }}
tags:
  - decision
  - adr
summary: "{{ decision_id }}: {{ decision[:100] }}"
created: {{ now.strftime('%Y-%m-%d') }}
status: {{ status | default('accepted') }}
---

# {{ decision_id }}: {{ title }}

**Status:** {{ status | default('accepted') }}
**Decisor:** {{ made_by | default('manager') }}
**Data:** {{ now.strftime('%Y-%m-%d') }}

## Contexto
{{ context }}

## Decisão
{{ decision }}

## Racional
{{ rationale }}

## Alternativas Consideradas
{% for alt in alternatives %}
- {{ alt }}
{% else %}
N/A
{% endfor %}

## Consequências
{% for con in consequences %}
- {{ con }}
{% else %}
A documentar conforme a decisão se materializa.
{% endfor %}
