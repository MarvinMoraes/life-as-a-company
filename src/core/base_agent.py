"""Classe base abstrata para todos os agentes da fábrica."""

from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..schemas.agent import AgentContextPack, AgentResponse
from ..schemas.task import AgentRole

if TYPE_CHECKING:
    from ..providers.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Contrato que todo agente deve implementar.

    Cada agente tem papel único, prompt próprio e política de memória.
    Agentes não conhecem uns aos outros — comunicam via Manager.
    """

    role: AgentRole
    name: str
    description: str

    def __init__(self, provider: "BaseLLMProvider", prompt: str) -> None:
        self.provider = provider
        self.system_prompt = prompt
        self._logger = logging.getLogger(f"agent.{self.role.value}")

    @abstractmethod
    async def execute(self, context_pack: AgentContextPack) -> AgentResponse:
        """Executa a tarefa descrita no context_pack e retorna uma AgentResponse."""
        ...

    def build_system_prompt(self, extra_context: str = "") -> str:
        """Monta o prompt de sistema com contexto adicional, se houver."""
        if not extra_context:
            return self.system_prompt
        return f"{self.system_prompt}\n\n---\n## Contexto Adicional\n{extra_context}"

    def _format_context_pack(self, pack: AgentContextPack) -> str:
        """Formata o context pack em texto para envio ao LLM."""
        sections = []
        for layer in pack.layers:
            sections.append(f"### [{layer.layer_name.upper()}]\n{layer.content}")
        return "\n\n".join(sections)

    def _make_user_message(self, pack: AgentContextPack) -> str:
        context_text = self._format_context_pack(pack)
        task = pack.task
        criteria = "\n".join(f"- {c}" for c in task.acceptance_criteria) or "- Entregar conforme formato solicitado"
        return (
            f"## Tarefa: {task.objective}\n\n"
            f"**Projeto:** {task.project_id}\n"
            f"**Profundidade esperada:** {task.max_response_depth}\n\n"
            f"### Critérios de Aceite\n{criteria}"
            + (f"\n\n### Contexto\n{context_text}" if context_text else "")
            + f"\n\n---\n**IMPORTANTE:** Responda APENAS com JSON válido seguindo o formato especificado no seu prompt de sistema. Sem texto antes ou depois do JSON. Sem blocos markdown."
        )

    @staticmethod
    def _parse_json(raw: str) -> dict:
        """Extrai JSON da resposta mesmo que venha em bloco markdown ou com texto ao redor."""
        # 1. Tenta direto
        try:
            return json.loads(raw.strip())
        except json.JSONDecodeError:
            pass

        # 2. Extrai conteúdo de bloco markdown ```json ... ``` ou ``` ... ```
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # 3. Extrai do primeiro { até o último } (JSON completo no texto)
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(raw[start : end + 1])
            except json.JSONDecodeError:
                pass

        # 4. Fallback — preserva conteúdo como texto para não perder informação
        return {"status": "partial", "raw_response": raw, "summary": raw[:300]}

    async def _call_provider(self, user_message: str, max_tokens: int = 2048) -> str:
        """Chama o provider LLM com o prompt de sistema do agente."""
        self._logger.debug("Chamando provider [%s] max_tokens=%d", self.provider.__class__.__name__, max_tokens)
        return await self.provider.complete(
            system=self.system_prompt,
            user=user_message,
            max_tokens=max_tokens,
        )
