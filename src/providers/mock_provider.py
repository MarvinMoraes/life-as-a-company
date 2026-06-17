
"""Provider mock para testes e desenvolvimento sem API externa."""

from __future__ import annotations

import json
import logging

from .base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)

# Respostas simuladas por padrão de palavra-chave no prompt do sistema
MOCK_RESPONSES: dict[str, str] = {
    "manager": json.dumps({
        "status": "success",
        "summary": "Mock: Manager analisou o objetivo e delegou tarefas.",
        "decisions": [{"title": "Iniciar com Product Strategist", "rationale": "Precisa de PRD antes de arquitetura técnica"}],
        "next_tasks": ["product_discovery", "market_research"]
    }),
    "engineer": json.dumps({
        "status": "success",
        "summary": "Mock: Arquitetura definida com FastAPI + PostgreSQL + React.",
        "tech_stack": {"backend": "FastAPI", "db": "PostgreSQL", "frontend": "Next.js"},
        "implementation_phases": [
            {"phase": 1, "name": "MVP Backend", "effort": "2 semanas"},
            {"phase": 2, "name": "Frontend", "effort": "1 semana"}
        ]
    }),
    "product": json.dumps({
        "status": "success",
        "summary": "Mock: Discovery concluído. PRD v1.0 gerado.",
        "value_proposition": "Automatiza processos repetitivos para times de 5-50 pessoas.",
        "personas": [{"name": "Ana", "role": "Gestora de Projetos", "main_pain": "Tempo perdido em atualizações manuais"}]
    }),
    "marketing": json.dumps({
        "status": "success",
        "summary": "Mock: Go-to-market definido com foco em inbound + product-led growth.",
        "channels": ["SEO/Blog", "Product Hunt Launch", "LinkedIn Ads"],
        "positioning": "O único SaaS que combina automação com simplicidade de uso."
    }),
    "qa": json.dumps({
        "status": "success",
        "summary": "Mock: QA concluído. 2 gaps identificados, nenhum crítico.",
        "verdict": "approved_with_notes",
        "score": 7.5,
        "findings": [
            {"severity": "minor", "category": "doc_gap", "description": "Critérios de aceite do login social não especificados"}
        ]
    }),
}


class MockLLMProvider(BaseLLMProvider):
    """Simula respostas LLM baseadas no papel do agente.

    Útil para:
    - Testes de integração sem custo de API
    - Desenvolvimento de novos workflows
    - Smoke tests de CI/CD
    """

    provider_name = "mock"

    def __init__(self, latency_ms: int = 50) -> None:
        self.latency_ms = latency_ms
        self._call_count = 0

    async def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:
        import asyncio
        await asyncio.sleep(self.latency_ms / 1000)
        self._call_count += 1

        system_lower = system.lower()
        for keyword, response in MOCK_RESPONSES.items():
            if keyword in system_lower:
                logger.debug("MockProvider: retornando resposta simulada para '%s'", keyword)
                return response

        # Fallback genérico
        return json.dumps({
            "status": "success",
            "summary": f"Mock: tarefa processada (chamada #{self._call_count}).",
            "content": f"Resposta simulada para: {user[:100]}"
        })

    async def count_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)
