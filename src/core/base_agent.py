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
    from ..tools.executor import ToolExecutor

logger = logging.getLogger(__name__)

_MAX_ITERATIONS = 10


class BaseAgent(ABC):
    """Contrato que todo agente deve implementar.

    Cada agente tem papel único, prompt próprio e política de memória.
    Agentes não conhecem uns aos outros — comunicam via Manager.
    Quando tool_executor está presente, usa loop agêntico com tool use.
    """

    role: AgentRole
    name: str
    description: str

    def __init__(
        self,
        provider: "BaseLLMProvider",
        prompt: str,
        tool_executor: "ToolExecutor | None" = None,
    ) -> None:
        self.provider = provider
        self.system_prompt = prompt
        self.tool_executor = tool_executor
        self._logger = logging.getLogger(f"agent.{self.role.value}")

    @abstractmethod
    async def execute(self, context_pack: AgentContextPack) -> AgentResponse:
        """Executa a tarefa descrita no context_pack e retorna uma AgentResponse."""
        ...

    # ------------------------------------------------------------------
    # Loop agêntico (tool use)
    # ------------------------------------------------------------------

    async def _run_agentic_loop(
        self,
        user_message: str,
        tools: list[dict],
        max_tokens: int = 4096,
    ) -> str:
        """Executa o loop agêntico: LLM → tool call → resultado → LLM → ...

        Termina quando stop_reason == 'end_turn' ou após _MAX_ITERATIONS.
        Emite eventos ao EventBus global para display na CLI.
        """
        from ..events import AgentEvent, EventBus, EventType

        bus = EventBus.global_bus()
        messages: list[dict] = [{"role": "user", "content": user_message}]

        for iteration in range(_MAX_ITERATIONS):
            response = await self.provider.complete_with_tools(
                system=self.system_prompt,
                messages=messages,
                tools=tools,
                max_tokens=max_tokens,
                use_cache=True,
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                return self._extract_text(response.content)

            if response.stop_reason == "tool_use":
                tool_results: list[dict] = []

                for block in response.content:
                    if getattr(block, "type", None) != "tool_use":
                        continue

                    tool_name = block.name
                    tool_input = block.input

                    bus.emit(AgentEvent(
                        event_type=EventType.TOOL_CALL,
                        agent_role=self.role.value,
                        data={"tool": tool_name, "input": tool_input, "iteration": iteration + 1},
                    ))

                    result = await self.tool_executor.execute(tool_name, tool_input)

                    bus.emit(AgentEvent(
                        event_type=EventType.TOOL_RESULT,
                        agent_role=self.role.value,
                        data={"tool": tool_name, "result": result[:300]},
                    ))

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

                messages.append({"role": "user", "content": tool_results})
            else:
                self._logger.warning("stop_reason inesperado: %s", response.stop_reason)
                return self._extract_text(response.content)

        self._logger.warning("Loop agêntico atingiu max_iterations=%d", _MAX_ITERATIONS)
        return self._extract_text(messages[-1].get("content", []))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def build_system_prompt(self, extra_context: str = "") -> str:
        if not extra_context:
            return self.system_prompt
        return f"{self.system_prompt}\n\n---\n## Contexto Adicional\n{extra_context}"

    def _format_context_pack(self, pack: AgentContextPack) -> str:
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
            + "\n\n---\n**IMPORTANTE:** Responda APENAS com JSON válido seguindo o formato especificado no seu prompt de sistema. Sem texto antes ou depois do JSON. Sem blocos markdown."
        )

    def _make_user_message_for_tools(self, pack: AgentContextPack) -> str:
        """Versão da mensagem para agentes com tool use — instrução aberta no fim."""
        context_text = self._format_context_pack(pack)
        task = pack.task
        criteria = "\n".join(f"- {c}" for c in task.acceptance_criteria) or "- Entregar conforme formato solicitado"
        return (
            f"## Tarefa: {task.objective}\n\n"
            f"**Projeto:** {task.project_id}\n"
            f"**Profundidade esperada:** {task.max_response_depth}\n\n"
            f"### Critérios de Aceite\n{criteria}"
            + (f"\n\n### Contexto\n{context_text}" if context_text else "")
            + "\n\n---\nUse as tools disponíveis para executar a tarefa. Ao terminar, responda em JSON conforme seu formato de saída."
        )

    @staticmethod
    def _extract_text(content: object) -> str:
        """Extrai texto de content blocks da Anthropic (lista ou string)."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            texts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    texts.append(block.get("text", ""))
                elif hasattr(block, "type") and block.type == "text":
                    texts.append(block.text)
            return "\n".join(texts)
        return str(content)

    @staticmethod
    def _parse_json(raw: str) -> dict:
        """Extrai JSON da resposta mesmo que venha em bloco markdown ou com texto ao redor."""
        try:
            return json.loads(raw.strip())
        except json.JSONDecodeError:
            pass

        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(raw[start : end + 1])
            except json.JSONDecodeError:
                pass

        return {"status": "partial", "raw_response": raw, "summary": raw[:300]}

    async def _call_provider(self, user_message: str, max_tokens: int = 2048) -> str:
        self._logger.debug("Chamando provider [%s] max_tokens=%d", self.provider.__class__.__name__, max_tokens)
        return await self.provider.complete(
            system=self.system_prompt,
            user=user_message,
            max_tokens=max_tokens,
        )
