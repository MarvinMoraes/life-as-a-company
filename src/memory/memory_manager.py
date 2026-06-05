"""Gerenciador de memória — interface unificada para leitura/escrita no vault."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from ..schemas.memory import DecisionRecord, MemoryNote, MemoryType

logger = logging.getLogger(__name__)


class MemoryManager:
    """Camada de acesso à memória markdown do vault Obsidian.

    Separa dois tipos de memória:
    - Canônica: notas permanentes (decisões, PRDs, planos)
    - Operacional: snapshots e logs de execução (podem ser purgados)
    """

    def __init__(self, vault_path: Path) -> None:
        self.vault = vault_path
        self._cache: dict[str, MemoryNote] = {}

    async def get_note(self, slug: str) -> Optional[MemoryNote]:
        """Recupera nota por slug. Usa cache em memória para evitar I/O repetido."""
        if slug in self._cache:
            return self._cache[slug]

        from ..obsidian.reader import ObsidianReader
        reader = ObsidianReader(self.vault)
        note = await reader.read(slug)
        if note:
            self._cache[slug] = note
        return note

    async def save_note(self, note: MemoryNote) -> Path:
        """Persiste nota no vault e atualiza cache."""
        from ..obsidian.writer import ObsidianWriter
        writer = ObsidianWriter(self.vault)
        path = await writer.write(note)
        self._cache[note.slug] = note
        logger.info("Nota salva: %s → %s", note.slug, path)
        return path

    async def save_decision(self, record: DecisionRecord) -> Path:
        """Converte DecisionRecord em MemoryNote e salva."""
        note = MemoryNote(
            slug=record.decision_id.lower(),
            title=f"{record.decision_id}: {record.title}",
            type=MemoryType.DECISION,
            project_id=record.project_id,
            tags=["decision", "adr"],
            content=record.to_markdown(),
            summary=f"{record.decision_id}: {record.decision[:120]}",
        )
        return await self.save_note(note)

    async def search(
        self,
        query: str,
        project_id: Optional[str] = None,
        note_type: Optional[MemoryType] = None,
        limit: int = 5,
    ) -> list[MemoryNote]:
        """Busca notas relevantes por palavra-chave e filtros.

        Implementação atual: busca simples em arquivos. Fase 2 pode adicionar embeddings.
        """
        from ..obsidian.reader import ObsidianReader
        reader = ObsidianReader(self.vault)
        all_notes = await reader.list_notes(project_id=project_id, note_type=note_type)

        query_lower = query.lower()
        scored: list[tuple[float, MemoryNote]] = []

        for note in all_notes:
            score = 0.0
            if query_lower in note.title.lower():
                score += 3.0
            if query_lower in note.summary.lower():
                score += 2.0
            if any(query_lower in tag for tag in note.tags):
                score += 1.0
            if score > 0:
                scored.append((score, note))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [note for _, note in scored[:limit]]

    async def get_project_digest(self, project_id: str) -> str:
        """Retorna um digest compacto de toda a memória de um projeto."""
        from ..obsidian.reader import ObsidianReader
        reader = ObsidianReader(self.vault)
        notes = await reader.list_notes(project_id=project_id)

        if not notes:
            return f"Nenhuma nota encontrada para projeto '{project_id}'."

        lines = [f"# Memory Digest: {project_id}\n"]
        for note in notes[:10]:  # top 10 para não explodir contexto
            lines.append(f"## [{note.type.value}] {note.title}")
            lines.append(note.summary or note.content[:200])
            lines.append("")

        return "\n".join(lines)

    def invalidate_cache(self, slug: Optional[str] = None) -> None:
        if slug:
            self._cache.pop(slug, None)
        else:
            self._cache.clear()
