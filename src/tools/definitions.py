"""Definições de tools para a Anthropic API, por AgentRole."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..schemas.task import AgentRole

# ---------------------------------------------------------------------------
# Tools nativas (file I/O + shell + delegation)
# ---------------------------------------------------------------------------

_READ_FILE = {
    "name": "read_file",
    "description": "Lê o conteúdo de um arquivo. O path é relativo à raiz permitida para o agente.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Caminho relativo ao escopo do agente (ex: src/app/page.tsx)"},
            "max_lines": {"type": "integer", "description": "Número máximo de linhas a retornar (default: 200)", "default": 200},
        },
        "required": ["path"],
    },
}

_WRITE_FILE = {
    "name": "write_file",
    "description": "Escreve (cria ou sobrescreve) um arquivo. O path é relativo à raiz permitida.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Caminho relativo ao escopo do agente"},
            "content": {"type": "string", "description": "Conteúdo completo do arquivo"},
        },
        "required": ["path", "content"],
    },
}

_LIST_FILES = {
    "name": "list_files",
    "description": "Lista arquivos em um diretório usando glob pattern.",
    "input_schema": {
        "type": "object",
        "properties": {
            "directory": {"type": "string", "description": "Diretório relativo ao escopo (ex: src/components)", "default": "."},
            "pattern": {"type": "string", "description": "Glob pattern (ex: **/*.tsx, *.md)", "default": "**/*"},
        },
        "required": [],
    },
}

_RUN_COMMAND = {
    "name": "run_command",
    "description": "Executa um comando permitido no diretório do projeto. Comandos disponíveis: npm run build, npm run lint, npm run dev.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Comando a executar",
                "enum": ["npm run build", "npm run lint", "npm run dev"],
            },
        },
        "required": ["command"],
    },
}

_DELEGATE_TO_AGENT = {
    "name": "delegate_to_agent",
    "description": "Delega uma tarefa a um agente especializado (engineer, product, marketing, qa). Use quando o trabalho requer expertise específica.",
    "input_schema": {
        "type": "object",
        "properties": {
            "agent_role": {
                "type": "string",
                "description": "Papel do agente destino",
                "enum": ["engineer", "product", "marketing", "qa"],
            },
            "objective": {"type": "string", "description": "Objetivo claro em uma linha para o agente"},
            "context": {"type": "string", "description": "Contexto necessário para o agente executar a tarefa"},
        },
        "required": ["agent_role", "objective", "context"],
    },
}

# ---------------------------------------------------------------------------
# Tools via MCP (adicionadas dinamicamente se adapter disponível)
# ---------------------------------------------------------------------------

_GITHUB_LIST_ISSUES = {
    "name": "github_list_issues",
    "description": "Lista issues abertas do repositório GitHub do projeto.",
    "input_schema": {
        "type": "object",
        "properties": {
            "repo": {"type": "string", "description": "Repositório no formato owner/repo"},
            "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"},
            "limit": {"type": "integer", "default": 10},
        },
        "required": ["repo"],
    },
}

_GITHUB_CREATE_PR = {
    "name": "github_create_pull_request",
    "description": "Cria um Pull Request no GitHub.",
    "input_schema": {
        "type": "object",
        "properties": {
            "repo": {"type": "string", "description": "Repositório no formato owner/repo"},
            "title": {"type": "string"},
            "body": {"type": "string"},
            "head": {"type": "string", "description": "Branch de origem"},
            "base": {"type": "string", "description": "Branch destino (default: main)", "default": "main"},
        },
        "required": ["repo", "title", "body", "head"],
    },
}

_GITHUB_SEARCH_CODE = {
    "name": "github_search_code",
    "description": "Pesquisa código em repositórios GitHub.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Termo de busca"},
            "repo": {"type": "string", "description": "Restringir ao repositório owner/repo (opcional)"},
        },
        "required": ["query"],
    },
}

_WEB_SEARCH = {
    "name": "web_search",
    "description": "Pesquisa na web para market research, análise de concorrentes, tendências de produto.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Consulta de busca"},
            "count": {"type": "integer", "description": "Número de resultados (default: 5)", "default": 5},
        },
        "required": ["query"],
    },
}

# ---------------------------------------------------------------------------
# Mapeamento por role
# ---------------------------------------------------------------------------

_NATIVE_TOOLS_BY_ROLE: dict[str, list[dict]] = {
    "manager":   [_DELEGATE_TO_AGENT, _READ_FILE, _WRITE_FILE],
    "engineer":  [_READ_FILE, _WRITE_FILE, _LIST_FILES, _RUN_COMMAND],
    "product":   [_READ_FILE, _WRITE_FILE],
    "qa":        [_READ_FILE, _RUN_COMMAND],
    "marketing": [_READ_FILE, _WRITE_FILE],
}

_MCP_TOOLS_BY_ROLE: dict[str, list[dict]] = {
    "manager":   [_GITHUB_LIST_ISSUES, _GITHUB_CREATE_PR],
    "engineer":  [_GITHUB_CREATE_PR, _GITHUB_SEARCH_CODE],
    "product":   [_WEB_SEARCH],
    "qa":        [],
    "marketing": [_WEB_SEARCH],
}


def get_tool_definitions_for_role(
    role: "AgentRole",
    include_mcp: bool = False,
) -> list[dict]:
    """Retorna lista de tool definitions no formato Anthropic para o role dado."""
    role_key = role.value if hasattr(role, "value") else str(role)
    tools = list(_NATIVE_TOOLS_BY_ROLE.get(role_key, []))
    if include_mcp:
        tools.extend(_MCP_TOOLS_BY_ROLE.get(role_key, []))
    return tools


def get_mcp_tool_names_for_role(role: "AgentRole") -> set[str]:
    """Retorna os nomes das tools que precisam ser roteadas para MCP."""
    role_key = role.value if hasattr(role, "value") else str(role)
    return {t["name"] for t in _MCP_TOOLS_BY_ROLE.get(role_key, [])}
