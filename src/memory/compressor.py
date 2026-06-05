"""Compressão e sumarização de contexto para economia de tokens."""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


class ContextCompressor:
    """Estratégias de compressão para manter contexto dentro do budget.

    Princípios:
    - Preservar informação semântica, sacrificar formatação
    - Resumos progressivos: notas antigas viram summaries cada vez menores
    - Decisões são sempre preservadas integralmente
    - Logs operacionais são descartáveis após snapshot
    """

    @staticmethod
    def truncate(text: str, max_tokens: int, strategy: str = "end") -> str:
        """Trunca texto para caber em max_tokens.

        strategy:
        - "end"    — remove do final (padrão)
        - "middle" — remove do meio, preservando início e fim
        - "smart"  — remove parágrafos menos relevantes (heurística simples)
        """
        max_chars = max_tokens * 4  # ~4 chars/token
        if len(text) <= max_chars:
            return text

        if strategy == "end":
            return text[:max_chars] + "\n... [truncado]"

        if strategy == "middle":
            keep = max_chars // 2
            return text[:keep] + "\n... [omitido] ...\n" + text[-keep:]

        if strategy == "smart":
            return ContextCompressor._smart_truncate(text, max_chars)

        return text[:max_chars]

    @staticmethod
    def _smart_truncate(text: str, max_chars: int) -> str:
        """Remove parágrafos mais curtos/menos informativos até caber."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        while sum(len(p) for p in paragraphs) > max_chars and len(paragraphs) > 1:
            # Remove o parágrafo mais curto (heurística: menos informativo)
            shortest_idx = min(range(len(paragraphs)), key=lambda i: len(paragraphs[i]))
            paragraphs.pop(shortest_idx)
        return "\n\n".join(paragraphs)

    @staticmethod
    def summarize_conversation(messages: list[dict], keep_last_n: int = 3) -> tuple[str, list[dict]]:
        """Comprime histórico de mensagens: resume antigas, mantém N recentes.

        Returns:
            (summary_text, recent_messages)
        """
        if len(messages) <= keep_last_n:
            return "", messages

        to_summarize = messages[:-keep_last_n]
        recent = messages[-keep_last_n:]

        summary_lines = []
        for msg in to_summarize:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            first_line = content.split("\n")[0][:100]
            summary_lines.append(f"[{role}] {first_line}")

        summary = "# Histórico Resumido\n" + "\n".join(summary_lines)
        return summary, recent

    @staticmethod
    def extract_key_decisions(text: str) -> list[str]:
        """Extrai decisões-chave de um texto usando padrões simples."""
        patterns = [
            r"(?:decidimos?|escolhemos?|optamos? por|vamos usar|será)\s+(.{10,100}?)(?:\.|$)",
            r"(?:Decisão|Decision|DECISÃO):\s*(.{10,200}?)(?:\n|$)",
        ]
        decisions = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            decisions.extend(m.strip() for m in matches)
        return list(dict.fromkeys(decisions))  # deduplica mantendo ordem

    @staticmethod
    def compress_note_for_context(content: str, max_tokens: int = 150) -> str:
        """Comprime uma nota para inclusão compacta em context packs."""
        max_chars = max_tokens * 4
        # Prioriza: título + primeiro parágrafo + lista de bullets
        lines = content.split("\n")
        important: list[str] = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("-") or stripped.startswith("*"):
                important.append(stripped)
            elif important and len("\n".join(important)) < max_chars // 2:
                important.append(stripped)

        compressed = "\n".join(important)
        return ContextCompressor.truncate(compressed, max_tokens, strategy="end")
