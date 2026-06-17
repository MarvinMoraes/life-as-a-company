"""Debug do parser JSON e dos token limits dos agentes."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()


async def main():
    from src.config import get_settings
    from src.core.base_agent import BaseAgent
    from src.providers.claude_provider import ClaudeLLMProvider

    settings = get_settings()
    provider = ClaudeLLMProvider(api_key=settings.anthropic_api_key)

    # 1. Testa se o parser consegue extrair JSON com backticks
    print("=== Teste 1: Parser com markdown ===")
    samples = [
        '```json\n{"status": "success", "msg": "ok"}\n```',
        '{"status": "success"}',
        'Aqui está o resultado:\n```json\n{"a": 1, "b": 2}\n```\nEspero que ajude.',
        'resultado: {"x": 1}',
    ]
    for s in samples:
        result = BaseAgent._parse_json(s)
        print(f"  Input: {s[:60]!r}")
        print(f"  Output status: {result.get('status', 'parsed')} | keys: {list(result.keys())}\n")

    # 2. Testa resposta real do Claude
    print("=== Teste 2: Claude raw response ===")
    raw = await provider.complete(
        system="Voce e um agente de produto. Responda APENAS com JSON valido, sem texto adicional.",
        user='Retorne um JSON com campos: status, summary, features (lista com 2 itens).',
        max_tokens=512,
    )
    print(f"Raw (primeiros 300 chars):\n{raw[:300]}")
    print()
    parsed = BaseAgent._parse_json(raw)
    print(f"Parsed keys: {list(parsed.keys())}")
    print(f"Status: {parsed.get('status')}")


if __name__ == "__main__":
    asyncio.run(main())
