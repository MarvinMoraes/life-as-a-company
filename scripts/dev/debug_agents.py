"""Debug individual dos agentes Product e Marketing."""

import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()


async def main():
    from src.config import get_settings
    from src.core.base_agent import BaseAgent
    from src.providers.claude_provider import ClaudeLLMProvider
    from src.prompts.loader import PromptLoader
    from src.schemas.task import AgentRole

    settings = get_settings()
    provider = ClaudeLLMProvider(api_key=settings.anthropic_api_key)
    prompt = PromptLoader.load(AgentRole.PRODUCT)

    raw = await provider.complete(
        system=prompt,
        user=(
            "## Tarefa: Realizar discovery completo e gerar PRD v1.0\n\n"
            "**Projeto:** vitalflow\n"
            "**Profundidade esperada:** deep\n\n"
            "Ideia: SaaS de gestao pessoal integrada com saude, habitos, gamificacao e relatorios diarios/semanais/mensais.\n\n"
            "**IMPORTANTE:** Responda APENAS com JSON valido seguindo o formato do seu prompt. Sem texto antes ou depois do JSON."
        ),
        max_tokens=4000,
    )

    print(f"Tamanho da resposta: {len(raw)} chars")
    print(f"Inicio: {raw[:150]!r}")
    print(f"Fim: {raw[-100:]!r}")
    print()

    parsed = BaseAgent._parse_json(raw)
    print(f"Status: {parsed.get('status')}")
    print(f"Keys: {list(parsed.keys())}")
    if "value_proposition" in parsed:
        print(f"Value prop: {parsed['value_proposition'][:100]}")
    if "raw_response" in parsed:
        print("!!! FALLBACK ATIVADO")
        print(f"Reason: JSON nao parseado. Raw[:200]: {parsed['raw_response'][:200]!r}")


if __name__ == "__main__":
    asyncio.run(main())
