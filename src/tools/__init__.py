"""Tool use layer — file ops, shell, MCP adapters e delegation."""

from .definitions import get_tool_definitions_for_role
from .executor import ToolExecutor

__all__ = ["ToolExecutor", "get_tool_definitions_for_role"]
