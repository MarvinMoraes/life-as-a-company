"""Leitura e busca de notas do vault Obsidian."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

from ..schemas.memory import MemoryNote, MemoryType

logger = logging.getLogger(__name__)

FOLDER_TO_TYPE: dict[str, MemoryType] = {
    "Projects": MemoryType.PROJECT,
    "Decisions": MemoryType.DECISION,
    "PRDs": MemoryType.PRD,
    "Research": MemoryType.RESEARCH,
    "Marketing": MemoryType.MARKETING,
    "QA": MemoryType.QA,
    "Snapshots": MemoryType.SNAPSHOT,
    "Agents": MemoryType.AGENT_LOG,
    "Scratchpad": MemoryType.SCRATCH,
}


class ObsidianReader:
    """Lê e busca notas do vault Obsidian."""

    def __init__(self, vault_path: Path) -> None:
        self.vault = vault_path

    async def read(self, slug: str) -> Optional[MemoryNote]:
        """Localiza e lê uma nota pelo slug (nome do arquivo sem .md)."""
        found = list(self.vault.rglob(f"{slug}.md"))
        if not found:
            return None

        path = found[0]
        return self._parse(path)

    async def list_notes(
        self,
        project_id: Optional[str] = None,
        note_type: Optional[MemoryType] = None,
        limit: int = 50,
    ) -> list[MemoryNote]:
        """Lista notas com filtros opcionais."""
        notes: list[MemoryNote] = []

        # Determina diretórios de busca
        if note_type:
            from .writer import TYPE_TO_FOLDER
            folder_name = TYPE_TO_FOLDER.get(note_type, "Scratchpad")
            if project_id:
                search_dirs = [self.vault / folder_name / project_id]
            else:
                search_dirs = [self.vault / folder_name]
        elif project_id:
            search_dirs = [d for d in self.vault.rglob(project_id) if d.is_dir()]
        else:
            search_dirs = [self.vault]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            for md_file in sorted(search_dir.rglob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
                if len(notes) >= limit:
                    break
                note = self._parse(md_file)
                if note:
                    notes.append(note)

        return notes[:limit]

    def _parse(self, path: Path) -> Optional[MemoryNote]:
        """Parseia um arquivo .md com frontmatter YAML."""
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return None

        frontmatter, body = self._split_frontmatter(text)
        slug = path.stem

        # Infere o tipo pela pasta pai
        note_type = MemoryType.SCRATCH
        for part in path.parts:
            if part in FOLDER_TO_TYPE:
                note_type = FOLDER_TO_TYPE[part]
                break

        title = frontmatter.get("title", self._extract_h1(body) or slug)
        summary = frontmatter.get("summary", "")
        project_id = frontmatter.get("project_id")
        tags = frontmatter.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]

        # Extrai links Obsidian [[slug]]
        links = re.findall(r"\[\[([^\]]+)\]\]", body)

        return MemoryNote(
            slug=slug,
            title=title,
            type=note_type,
            project_id=project_id if project_id not in (None, "~", "null") else None,
            tags=tags,
            content=body.strip(),
            summary=summary,
            links=list(set(links)),
        )

    @staticmethod
    def _split_frontmatter(text: str) -> tuple[dict, str]:
        """Separa frontmatter YAML do corpo da nota."""
        if not text.startswith("---"):
            return {}, text

        end = text.find("---", 3)
        if end == -1:
            return {}, text

        fm_text = text[3:end].strip()
        body = text[end + 3:].strip()

        # Parser YAML mínimo (sem dependência de yaml)
        fm: dict = {}
        current_key: Optional[str] = None
        list_mode = False

        for line in fm_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("- ") and list_mode and current_key:
                if not isinstance(fm[current_key], list):
                    fm[current_key] = []
                fm[current_key].append(stripped[2:].strip())
            elif ":" in stripped:
                key, _, value = stripped.partition(":")
                key = key.strip()
                value = value.strip()
                if value:
                    fm[key] = value
                    list_mode = False
                else:
                    fm[key] = []
                    list_mode = True
                current_key = key

        return fm, body

    @staticmethod
    def _extract_h1(body: str) -> Optional[str]:
        match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        return match.group(1).strip() if match else None
