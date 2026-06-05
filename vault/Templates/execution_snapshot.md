---
title: "Snapshot: {{ workflow_name }} [{{ project_id }}]"
type: snapshot
project_id: {{ project_id }}
tags:
  - snapshot
  - {{ workflow_name }}
  - {{ status }}
summary: "{{ workflow_name }} [{{ status }}] — {{ steps_completed | length }} steps"
created: {{ now.strftime('%Y-%m-%d') }}
status: {{ status }}
---

# Execution Snapshot: {{ workflow_name }}

**Projeto:** {{ project_id }}
**Status:** {{ status }}
**ID:** {{ snapshot_id }}
**Iniciado:** {{ started_at }}
**Tokens usados:** {{ token_budget_used }}

## Steps Concluídos
{% for step in steps_completed %}
- ✓ {{ step }}
{% endfor %}

{% if steps_pending %}
## Steps Pendentes
{% for step in steps_pending %}
- ○ {{ step }}
{% endfor %}
{% endif %}

## Artefatos Gerados
```json
{{ artifacts | tojson(indent=2) }}
```

{% if error %}
## Erro
{{ error }}
{% endif %}
