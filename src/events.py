"""EventBus global — pub/sub para comunicação entre agentes e CLI."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class EventType(str, Enum):
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    DELEGATION = "delegation"
    WORKFLOW_STEP = "workflow_step"
    ERROR = "error"
    MESSAGE = "message"


@dataclass
class AgentEvent:
    event_type: EventType
    agent_role: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class EventBus:
    """Singleton pub/sub. Zero dependências de agentes — seguro para importar de qualquer lugar."""

    _global: EventBus | None = None

    def __init__(self) -> None:
        self._handlers: list[Callable[[AgentEvent], None]] = []

    @classmethod
    def global_bus(cls) -> EventBus:
        if cls._global is None:
            cls._global = cls()
        return cls._global

    @classmethod
    def reset(cls) -> None:
        cls._global = None

    def subscribe(self, handler: Callable[[AgentEvent], None]) -> None:
        self._handlers.append(handler)

    def unsubscribe(self, handler: Callable[[AgentEvent], None]) -> None:
        self._handlers = [h for h in self._handlers if h is not handler]

    def emit(self, event: AgentEvent) -> None:
        for handler in self._handlers:
            try:
                handler(event)
            except Exception:
                pass  # erros da UI nunca devem derrubar agentes
