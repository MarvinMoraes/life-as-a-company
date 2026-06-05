"""Escrita de notas no vault Obsidian em formato markdown com frontmatter."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from ..schemas.memory import MemoryNote, MemoryType

logger = logging.getLogger(__name__)

# Mapeamento de tipo → subpasta do vault
TYPE_TO_FOLDER: dict[MemoryType, str] = {
    MemoryType.PROJECT: "Projects",
    MemoryType.DECISION: "Decisions",
    MemoryType.PRD: "PRDs",
    MemoryType.RESEARCH: "Research",
    MemoryType.MARKETING: "Marketing",
    MemoryType.QA: "QA",
    MemoryType.SNAPSHOT: "Snapshots",
    MemoryType.AGENT_LOG: "Agents",
    MemoryType.SCRATCH: "Scratchpad",
}


class ObsidianWriter:
    """Escreve MemoryNotes como arquivos .md com frontmatter YAML."""

    def __init__(self, vault_path: Path) -> None:
        self.vault = vault_path

    async def write(self, note: MemoryNote) -> Path:
        """Escreve nota no vault. Cria diretórios se necessário."""
        folder = TYPE_TO_FOLDER.get(note.type, "Scratchpad")

        # Se tem project_id, cria subpasta por projeto
        if note.project_id:
            target_dir = self.vault / folder / note.project_id
        else:
            target_dir = self.vault / folder

        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / f"{note.slug}.md"

        content = self._render(note)
        file_path.write_text(content, encoding="utf-8")
        logger.debug("ObsidianWriter: escreveu %s", file_path)
        return file_path

    def _render(self, note: MemoryNote) -> str:
        """Renderiza nota com frontmatter YAML + corpo markdown."""
        fm = note.to_frontmatter_dict()
        frontmatter_lines = ["---"]
        for k, v in fm.items():
            if isinstance(v, list):
                if v:
                    frontmatter_lines.append(f"{k}:")
                    for item in v:
                        frontmatter_lines.append(f"  - {item}")
                else:
                    frontmatter_lines.append(f"{k}: []")
            elif v is None:
                frontmatter_lines.append(f"{k}: ~")
            else:
                frontmatter_lines.append(f"{k}: {v}")
        frontmatter_lines.append("---")
        frontmatter = "\n".join(frontmatter_lines)

        # Backlinks Obsidian
        links_section = ""
        if note.links:
            links_section = "\n\n---\n## Links\n" + " ".join(f"[[{l}]]" for l in note.links)

        return f"{frontmatter}\n\n# {note.title}\n\n{note.content}{links_section}\n"

    async def write_from_template(
        self,
        template_slug: str,
        variables: dict,
        output_slug: str,
        note_type: MemoryType,
        project_id: str | None = None,
    ) -> Path:
        """Renderiza um template do vault e salva como nova nota."""
        template_path = self.vault / "Templates" / f"{template_slug}.md"
        if not template_path.exists():
            raise FileNotFoundError(f"Template não encontrado: {template_path}")

        from jinja2 import Template
        template_text = template_path.read_text(encoding="utf-8")
        rendered_body = Template(template_text).render(**variables, now=datetime.utcnow())

        note = MemoryNote(
            slug=output_slug,
            title=variables.get("title", output_slug),
            type=note_type,
            project_id=project_id,
            tags=variables.get("tags", []),
            content=rendered_body,
            summary=variables.get("summary", ""),
        )
        return await self.write(note)
