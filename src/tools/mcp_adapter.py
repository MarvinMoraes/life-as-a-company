"""MCPToolAdapter — conecta a servidores MCP externos via stdio transport."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MCPToolAdapter:
    """Conecta a um servidor MCP (subprocesso stdio) e expõe suas tools.

    Uso:
        adapter = MCPToolAdapter("github")
        await adapter.start(["npx", "-y", "@modelcontextprotocol/server-github"], env={"GITHUB_TOKEN": token})
        tools = await adapter.list_tools()
        result = await adapter.call_tool("create_pull_request", {...})
        await adapter.close()
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._proc: asyncio.subprocess.Process | None = None
        self._req_id = 0
        self._tools_cache: list[dict] | None = None
        self._lock = asyncio.Lock()

    async def start(self, server_command: list[str], env: dict[str, str] | None = None) -> bool:
        """Inicia o servidor MCP. Retorna False se falhar (graceful degradation)."""
        merged_env = {**os.environ, **(env or {})}
        try:
            self._proc = await asyncio.create_subprocess_exec(
                *server_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
                env=merged_env,
            )
            # Handshake MCP: initialize
            await self._send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "saas-factory", "version": "1.0"},
            })
            await self._send_notification("notifications/initialized", {})
            logger.info("MCP adapter '%s' iniciado", self.name)
            return True
        except Exception as e:
            logger.warning("MCP adapter '%s' falhou ao iniciar: %s", self.name, e)
            self._proc = None
            return False

    @property
    def is_running(self) -> bool:
        return self._proc is not None and self._proc.returncode is None

    async def list_tools(self) -> list[dict]:
        """Retorna tool definitions no formato Anthropic."""
        if self._tools_cache is not None:
            return self._tools_cache
        if not self.is_running:
            return []
        try:
            response = await self._send_request("tools/list", {})
            raw_tools = response.get("result", {}).get("tools", [])
            self._tools_cache = [self._convert_to_anthropic_format(t) for t in raw_tools]
            return self._tools_cache
        except Exception as e:
            logger.warning("Falha ao listar tools do MCP '%s': %s", self.name, e)
            return []

    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        """Chama uma tool no servidor MCP e retorna resultado como string."""
        if not self.is_running:
            return f"ERROR: MCP adapter '{self.name}' não está rodando"
        try:
            response = await self._send_request("tools/call", {
                "name": tool_name,
                "arguments": arguments,
            })
            result = response.get("result", {})
            content = result.get("content", [])
            texts = [c.get("text", "") for c in content if c.get("type") == "text"]
            return "\n".join(texts) or json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return f"ERROR: MCP tool '{tool_name}' falhou: {e}"

    async def close(self) -> None:
        if self._proc and self._proc.returncode is None:
            try:
                self._proc.terminate()
                await asyncio.wait_for(self._proc.wait(), timeout=5.0)
            except Exception:
                self._proc.kill()
        self._proc = None

    # ------------------------------------------------------------------
    # JSON-RPC over stdio
    # ------------------------------------------------------------------

    async def _send_request(self, method: str, params: dict) -> dict:
        async with self._lock:
            self._req_id += 1
            message = {
                "jsonrpc": "2.0",
                "id": self._req_id,
                "method": method,
                "params": params,
            }
            await self._write(message)
            return await asyncio.wait_for(self._read_response(self._req_id), timeout=30.0)

    async def _send_notification(self, method: str, params: dict) -> None:
        message = {"jsonrpc": "2.0", "method": method, "params": params}
        await self._write(message)

    async def _write(self, message: dict) -> None:
        if not self._proc or not self._proc.stdin:
            raise RuntimeError("MCP process não está rodando")
        line = json.dumps(message, ensure_ascii=False) + "\n"
        self._proc.stdin.write(line.encode())
        await self._proc.stdin.drain()

    async def _read_response(self, req_id: int) -> dict:
        if not self._proc or not self._proc.stdout:
            raise RuntimeError("MCP process não está rodando")
        while True:
            line = await self._proc.stdout.readline()
            if not line:
                raise RuntimeError("MCP process fechou stdout inesperadamente")
            try:
                msg = json.loads(line.decode().strip())
                if msg.get("id") == req_id:
                    if "error" in msg:
                        raise RuntimeError(f"MCP error: {msg['error']}")
                    return msg
                # Mensagem de outro request — ignora (simplificado)
            except json.JSONDecodeError:
                continue

    # ------------------------------------------------------------------
    # Conversão de formato
    # ------------------------------------------------------------------

    @staticmethod
    def _convert_to_anthropic_format(mcp_tool: dict) -> dict:
        """Converte tool definition do formato MCP para o formato Anthropic."""
        return {
            "name": mcp_tool.get("name", ""),
            "description": mcp_tool.get("description", ""),
            "input_schema": mcp_tool.get("inputSchema", {"type": "object", "properties": {}}),
        }


# ---------------------------------------------------------------------------
# Factory: cria adapters a partir das settings
# ---------------------------------------------------------------------------

async def create_mcp_adapters(settings: Any) -> dict[str, MCPToolAdapter]:
    """Inicializa MCPs configurados. Retorna dict vazio se não configurado.

    MCPs suportados (graceful degradation — apenas inicializa os que têm credenciais):
    - github          : @modelcontextprotocol/server-github (GITHUB_TOKEN)
    - brave-search    : @modelcontextprotocol/server-brave-search (BRAVE_API_KEY)
    - sequential-think: @modelcontextprotocol/server-sequential-thinking (sem key)
    - memory          : @modelcontextprotocol/server-memory (sem key)
    - git             : @modelcontextprotocol/server-git (sem key)
    """
    adapters: dict[str, MCPToolAdapter] = {}

    if settings.has_github_mcp:
        adapter = MCPToolAdapter("github")
        ok = await adapter.start(
            ["npx", "-y", "@modelcontextprotocol/server-github"],
            env={"GITHUB_TOKEN": settings.github_token},
        )
        if ok:
            adapters["github"] = adapter
            logger.info("MCP github ativo")

    if settings.has_brave_mcp:
        adapter = MCPToolAdapter("brave-search")
        ok = await adapter.start(
            ["npx", "-y", "@modelcontextprotocol/server-brave-search"],
            env={"BRAVE_API_KEY": settings.brave_api_key},
        )
        if ok:
            adapters["brave-search"] = adapter
            logger.info("MCP brave-search ativo")

    # MCPs sem key — inicializa se o pacote estiver instalado
    for name, cmd in [
        ("sequential-thinking", ["npx", "-y", "@modelcontextprotocol/server-sequential-thinking"]),
        ("memory", ["npx", "-y", "@modelcontextprotocol/server-memory"]),
        ("git", ["npx", "-y", "@modelcontextprotocol/server-git", "--repository", "."]),
    ]:
        adapter = MCPToolAdapter(name)
        ok = await adapter.start(cmd)
        if ok:
            adapters[name] = adapter
            logger.info("MCP %s ativo", name)

    return adapters


def get_adapter_for_tool(tool_name: str, adapters: dict[str, MCPToolAdapter]) -> MCPToolAdapter | None:
    """Roteia uma tool name para o adapter MCP correto."""
    if tool_name.startswith("github_") or tool_name == "github_create_pull_request":
        return adapters.get("github")
    if tool_name == "web_search":
        return adapters.get("brave-search")
    if tool_name == "sequential_thinking":
        return adapters.get("sequential-thinking")
    if tool_name in ("create_entities", "search_nodes", "add_observations"):
        return adapters.get("memory")
    if tool_name in ("git_diff", "git_log", "git_status", "git_blame"):
        return adapters.get("git")
    return None
