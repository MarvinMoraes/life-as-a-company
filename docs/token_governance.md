# Governança de Tokens

## Por que isso importa

Tokens são o recurso mais escasso da fábrica. Uma execução sem disciplina de contexto pode:
- Consumir 10-20x mais tokens que o necessário
- Exceder limites de contexto dos modelos
- Gerar respostas piores por excesso de ruído no contexto
- Aumentar custos de API desnecessariamente

## Camadas de Contexto

| Camada | Conteúdo | Budget | Prioridade |
|--------|----------|--------|------------|
| task | Objetivo + critérios de aceite | ~400 tokens | 1 (sempre) |
| agent | Papel e responsabilidades | ~200 tokens | 2 (sempre) |
| project | Visão + PRD + status | ~500 tokens | 3 (quando necessário) |
| memory | Notas relevantes do vault | ~600 tokens | 4 (seletivo) |
| global | Princípios da fábrica | ~300 tokens | 5 (se couber) |

**Budget total padrão:** 4.096 tokens
**Budget em modo compacto:** 2.048 tokens

## Regras do Manager

1. **Verificar vault antes de criar tarefa** — se já existe resposta, recuperar
2. **Usar `depth: short` para planejamento** — não precisa de resposta longa
3. **Passar apenas `memory_hints` específicos** — nunca `project_digest` inteiro
4. **Resumos progressivos** — contexto de steps anteriores entra como summary (max 500 chars)
5. **Não repetir contexto** — se o agente já recebeu no task layer, não repetir no project layer

## Políticas de Profundidade

### `depth: short`
- Tokens máximos na resposta: 512-768
- Usar para: confirmações, triagem, planejamento de alto nível
- Agentes: Manager (sempre), QA (triagem)

### `depth: medium`
- Tokens máximos na resposta: 1.024-2.048
- Usar para: análises, planos parciais, reviews
- Agentes: todos (padrão)

### `depth: deep`
- Tokens máximos na resposta: 2.048-4.096
- Usar para: PRD completo, arquitetura detalhada, auditoria
- Agentes: Product, Engineer, QA (auditoria)

## Estratégia de Compressão

### Histórico de Conversa
```python
# Ao invés de passar mensagens completas:
messages = [msg1, msg2, ..., msg50]

# Comprimir para summary + recentes:
summary, recent = ContextCompressor.summarize_conversation(messages, keep_last_n=3)
context = f"{summary}\n\n## Mensagens Recentes\n{format(recent)}"
```

### Notas do Vault
```python
# Ao invés de conteúdo completo:
note.content  # pode ter 2000+ tokens

# Usar summary compacto:
note.summary  # ~150 tokens, gerado na criação da nota
```

### Resultados de Workflows
```python
# Ao invés de passar resultado completo do step anterior:
step_inputs["_previous_results"] = {
    step_name: str(content)[:500]  # resumo compacto
}
```

## Estimativa de Custo

Com `DEFAULT_PROVIDER=claude` e `claude-sonnet-4-6`:
- Workflow idea-to-prd (5 steps): ~15.000-20.000 tokens input + ~8.000 output
- Workflow prd-to-build (4 steps): ~12.000-16.000 tokens input + ~6.000 output

Com provider mock (desenvolvimento): $0, latência <100ms.

## Otimizações Futuras (Fase 2)

1. **Embeddings** para recuperação semântica de memória (vs. busca por palavra-chave)
2. **Prompt caching** (Claude API) para system prompts estáticos
3. **Batching** de tarefas paralelas não-dependentes
4. **Cache de resultados** para queries idênticas ao vault
