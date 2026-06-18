"""ToolExecutor — despacha tool calls dos agentes com path scoping e allowlist de comandos."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Awaitable, Callable

if TYPE_CHECKING:
    from ..schemas.task import AgentRole

logger = logging.getLogger(__name__)

# No Windows, npm é um .cmd (batch script) — precisa de cmd /c para subprocess
_NPM = ["cmd", "/c", "npm"] if sys.platform == "win32" else ["npm"]

ALLOWED_COMMANDS: dict[str, list[str]] = {
    "npm run build": [*_NPM, "run", "build"],
    "npm run lint": [*_NPM, "run", "lint"],
    "npm run dev": [*_NPM, "run", "dev"],
}

_COMMAND_TIMEOUT = 120.0
_COMMAND_OUTPUT_LIMIT = 3000
_FILE_READ_LIMIT = 200


class ToolExecutor:
    """Executa tool calls vindos do loop agêntico.

    Cada instância é criada por role — o scope de paths é diferente por agente.
    """

    def __init__(
        self,
        vault_path: Path,
        flouwy_path: Path,
        role: "AgentRole",
        agent_caller: Callable[[str, str, str], Awaitable[dict]] | None = None,
        mcp_adapter: "MCPToolAdapter | None" = None,
    ) -> None:
        self.vault_path = vault_path.resolve()
        self.flouwy_path = flouwy_path.resolve()
        self.role = role
        self.agent_caller = agent_caller
        self.mcp_adapter = mcp_adapter
        self._logger = logging.getLogger(f"tools.{role.value if hasattr(role, 'value') else role}")

    # ------------------------------------------------------------------
    # Dispatch principal
    # ------------------------------------------------------------------

    async def execute(self, tool_name: str, tool_input: dict) -> str:
        self._logger.debug("Tool call: %s %s", tool_name, list(tool_input.keys()))
        try:
            match tool_name:
                case "read_file":
                    return await self._read_file(
                        tool_input["path"],
                        tool_input.get("max_lines", _FILE_READ_LIMIT),
                    )
                case "write_file":
                    return await self._write_file(tool_input["path"], tool_input["content"])
                case "list_files":
                    return await self._list_files(
                        tool_input.get("directory", "."),
                        tool_input.get("pattern", "**/*"),
                    )
                case "run_command":
                    return await self._run_command(tool_input["command"])
                case "delegate_to_agent":
                    return await self._delegate(
                        tool_input["agent_role"],
                        tool_input["objective"],
                        tool_input.get("context", ""),
                    )
                case _:
                    # Tenta rotear para MCP adapter
                    if self.mcp_adapter:
                        return await self.mcp_adapter.call_tool(tool_name, tool_input)
                    return f"ERROR: Tool desconhecida: '{tool_name}'"
        except PermissionError as e:
            return f"ERROR: Acesso negado — {e}"
        except asyncio.TimeoutError:
            return f"ERROR: Timeout ao executar '{tool_name}'"
        except Exception as e:
            self._logger.exception("Erro ao executar tool '%s'", tool_name)
            return f"ERROR: {type(e).__name__}: {e}"

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------

    def _resolve_safe(self, path_str: str, allowed_root: Path) -> Path:
        """Resolve path e verifica que está dentro do allowed_root."""
        resolved = (allowed_root / path_str).resolve()
        if not str(resolved).startswith(str(allowed_root)):
            raise PermissionError(f"Path fora do escopo permitido: {path_str!r} (root: {allowed_root})")
        return resolved

    def _allowed_read_roots(self) -> list[Path]:
        """Raízes de leitura permitidas por role."""
        role_key = self.role.value if hasattr(self.role, "value") else str(self.role)
        match role_key:
            case "engineer":
                return [self.flouwy_path]
            case "product":
                return [self.vault_path, self.flouwy_path]
            case "qa":
                return [self.flouwy_path]
            case "manager" | "marketing":
                return [self.vault_path]
            case _:
                return [self.vault_path]

    def _allowed_write_roots(self) -> list[Path]:
        """Raízes de escrita permitidas por role."""
        role_key = self.role.value if hasattr(self.role, "value") else str(self.role)
        match role_key:
            case "engineer":
                return [self.flouwy_path]
            case "product" | "manager" | "marketing":
                return [self.vault_path]
            case _:
                return []

    def _try_resolve(self, path_str: str, roots: list[Path]) -> Path:
        """Tenta resolver path em cada raiz; retorna a primeira que funcionar."""
        last_err: Exception | None = None
        for root in roots:
            try:
                return self._resolve_safe(path_str, root)
            except PermissionError as e:
                last_err = e
        if last_err:
            raise last_err
        raise PermissionError(f"Nenhuma raiz permitida para: {path_str!r}")

    async def _read_file(self, path_str: str, max_lines: int) -> str:
        resolved = self._try_resolve(path_str, self._allowed_read_roots())
        if not resolved.exists():
            return f"ERROR: Arquivo não encontrado: {path_str}"
        try:
            lines = resolved.read_text(encoding="utf-8").splitlines()
            total = len(lines)
            truncated = lines[:max_lines]
            result = "\n".join(truncated)
            if total > max_lines:
                result += f"\n\n[... {total - max_lines} linhas omitidas. Use max_lines maior se necessário.]"
            return result
        except UnicodeDecodeError:
            return f"ERROR: Arquivo binário — não pode ser lido como texto: {path_str}"

    async def _write_file(self, path_str: str, content: str) -> str:
        resolved = self._try_resolve(path_str, self._allowed_write_roots())
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")
        return f"OK: Arquivo escrito em {path_str} ({len(content)} bytes)"

    async def _list_files(self, directory: str, pattern: str) -> str:
        roots = self._allowed_read_roots()
        resolved_dir = self._try_resolve(directory, roots)
        if not resolved_dir.exists():
            return f"ERROR: Diretório não encontrado: {directory}"

        _EXCLUDE = {".next", "node_modules", ".git", "__pycache__", ".venv", "dist", "build", ".cache", ".turbo"}
        _LIMIT = 60

        matches: list[str] = []
        for p in resolved_dir.glob(pattern):
            if not p.is_file():
                continue
            rel = p.relative_to(roots[0])
            if any(part in _EXCLUDE for part in rel.parts):
                continue
            matches.append(str(rel))

        matches.sort()

        if not matches:
            return f"Nenhum arquivo encontrado em '{directory}' com pattern '{pattern}'"

        result = "\n".join(matches[:_LIMIT])
        if len(matches) > _LIMIT:
            result += f"\n\n[{len(matches) - _LIMIT} arquivos adicionais omitidos — refine o pattern ou use um subdiretório específico]"
        return result

    # ------------------------------------------------------------------
    # Shell
    # ------------------------------------------------------------------

    async def _run_command(self, command: str) -> str:
        if command not in ALLOWED_COMMANDS:
            allowed = list(ALLOWED_COMMANDS.keys())
            return f"ERROR: Comando não permitido: '{command}'. Permitidos: {allowed}"

        argv = ALLOWED_COMMANDS[command]
        self._logger.info("Executando: %s (cwd=%s)", command, self.flouwy_path)

        proc = await asyncio.create_subprocess_exec(
            *argv,
            cwd=str(self.flouwy_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        try:
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=_COMMAND_TIMEOUT)
        except asyncio.TimeoutError:
            proc.kill()
            return f"ERROR: Timeout ({_COMMAND_TIMEOUT}s) ao executar '{command}'"

        output = stdout.decode("utf-8", errors="replace")
        exit_code = proc.returncode
        truncated = output[:_COMMAND_OUTPUT_LIMIT]
        if len(output) > _COMMAND_OUTPUT_LIMIT:
            truncated += f"\n[... output truncado em {_COMMAND_OUTPUT_LIMIT} chars]"

        status = "OK" if exit_code == 0 else f"FAILED (exit {exit_code})"
        return f"{status}: {command}\n\n{truncated}"

    # ------------------------------------------------------------------
    # Delegation
    # ------------------------------------------------------------------

    async def _delegate(self, agent_role: str, objective: str, context: str) -> str:
        if not self.agent_caller:
            return "ERROR: Delegação não disponível (agent_caller não configurado)"
        self._logger.info("Delegando para %s: %s", agent_role, objective[:80])
        result = await self.agent_caller(agent_role, objective, context)
        return f"[{agent_role.upper()}] {result.get('summary', '')}\n\n{result.get('content', '')[:500]}"


# Importação tardia para evitar circular
try:
    from .mcp_adapter import MCPToolAdapter  # noqa: F401
except ImportError:
    pass
