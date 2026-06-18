---
slug: MARCUS
title: "Marcus Moraes — Perfil do Usuário"
type: user-profile
updated: 2026-06-17
---

# Marcus Moraes — Perfil do Usuário

> Lido por todos os agentes antes de qualquer ação.
> Este arquivo define quem é Marcus, como ele pensa e como trabalhar com ele.
> Agentes atualizam a seção "Preferências aprendidas" quando Marcus faz escolhas recorrentes.

---

## Identidade

- **Nome:** Marcus Moraes
- **Contexto cognitivo:** TDAH + autismo — processa melhor informação direta, estruturada, sem ambiguidade
- **Papel:** Fundador solo, PM + Engenheiro + Designer dos próprios produtos
- **ICP:** É o próprio cliente dos produtos que constrói — seu instinto sobre o produto é dado válido
- **Idioma:** Português brasileiro — todas as respostas em PT-BR, sempre
- **Localização:** Brasil

---

## Como Marcus pensa

- Prefere clareza a completude — uma resposta certa e curta vale mais que três longas
- Trabalha de forma iterativa e conversacional, não em cascata
- Decide rápido quando tem as opções bem apresentadas — não precisa de contexto extra
- Não separa vida pessoal de trabalho no contexto dos produtos — ele é o usuário
- Processa melhor em listas e tabelas do que em parágrafos longos
- Quanto mais tokens ele gastar lendo, menos energia sobra para decidir

---

## Regras de comunicação (inegociáveis)

- Sempre em português brasileiro
- Sem emojis em nenhuma circunstância
- Sem perguntas retóricas
- Sem recapitular o que acabou de ser dito
- Sem "ótima pergunta", "claro!", "com certeza" ou qualquer preâmbulo
- Resposta começa direto no conteúdo
- Chamar pelo nome: Marcus (não "você" em contexto de agente)
- Economizar tokens: sem texto decorativo, sem exemplos que não foram pedidos

---

## O que Marcus NÃO quer dos agentes

- Sugestões fora do backlog ativo (`spec/tasks.md`)
- Features que não têm REQ correspondente
- Decisões técnicas tomadas sem consulta quando impactam arquitetura
- Respostas que precisam de scroll para chegar no ponto
- Repetir informação que Marcus acabou de fornecer

---

## Contrato SDD

- Spec antes de código — sempre
- Se não tem REQ-NNN no `spec/requirements.md`, não existe como tarefa
- Toda decisão de arquitetura vai para `spec/design.md` antes de ser implementada
- Tasks são executadas na ordem do `spec/tasks.md` — não pular, não criar paralelas sem consulta
- Quando algo mudar durante implementação, atualizar a spec primeiro

---

## Projetos ativos

| Projeto | Status | Vault | Repo |
|---------|--------|-------|------|
| Flouwy | MVP em progresso | [[Projects/flouwy/SPEC]] | github.com/MarvinMoraes/flouwy |
| YouTube Kids Factory | Ativo | [[Projects/youtube-agent/SPEC]] | github.com/MarvinMoraes/youtube-agent |
| life-as-a-company | Sistema de agentes ativo | este vault | local |

---

## Preferências aprendidas

> Seção atualizada pelos agentes quando Marcus faz escolhas recorrentes.
> Formato: data — contexto — preferência observada

- 2026-06-07 — autenticação — preferência por email+senha sobre magic link (rate limit foi o gatilho, mas confirmou que prefere senha mesmo)
- 2026-06-07 — labels de UI — prefere abreviações de 3 letras para dias da semana (Dom/Seg/Ter) em vez de inicial única
- 2026-06-07 — score visual — prefere estado neutro (anel cinza) a estado de erro (vermelho) quando não há dado ainda
- 2026-06-07 — organização — prefere co-localização de artefatos por projeto em vez de por tipo de documento
- 2026-06-07 — agentes — prefere respostas diretas do Claude Code a acionar agentes via chat_manager para tarefas de código

---

## Links

- [[AGENTS]] — comportamento dos agentes neste vault
- [[_system/SDD_GUIDE]] — metodologia SDD adotada
- [[Projects/flouwy/SPEC]] — projeto principal ativo
- [[INDEX]] — catálogo completo do vault
