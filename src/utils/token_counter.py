"""Estimativa e controle de tokens."""

from __future__ import annotations


def estimate_tokens(text: str) -> int:
    """Estimativa rápida: ~4 chars por token (sem chamar API)."""
    return max(1, len(text) // 4)


def estimate_tokens_precise(text: str) -> int:
    """Estimativa precisa via tiktoken (se disponível)."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except ImportError:
        return estimate_tokens(text)


class TokenBudget:
    """Controla uso de tokens em uma execução."""

    def __init__(self, total: int) -> None:
        self.total = total
        self.used = 0

    @property
    def remaining(self) -> int:
        return max(0, self.total - self.used)

    @property
    def utilization(self) -> float:
        return self.used / self.total if self.total > 0 else 0.0

    def charge(self, tokens: int) -> bool:
        """Debita tokens. Retorna False se exceder budget."""
        if self.used + tokens > self.total:
            return False
        self.used += tokens
        return True

    def can_fit(self, text: str) -> bool:
        return self.charge(estimate_tokens(text))

    def __repr__(self) -> str:
        return f"TokenBudget({self.used}/{self.total} = {self.utilization:.1%})"
