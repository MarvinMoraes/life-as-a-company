"""Testes da camada de memória e Obsidian."""

import pytest
import tempfile
from pathlib import Path

from src.schemas.memory import MemoryNote, DecisionRecord, MemoryType
from src.obsidian.writer import ObsidianWriter
from src.obsidian.reader import ObsidianReader
from src.memory.compressor import ContextCompressor


@pytest.fixture
def tmp_vault(tmp_path):
    """Vault temporário para testes."""
    return tmp_path / "vault"


@pytest.mark.asyncio
async def test_write_and_read_note(tmp_vault):
    writer = ObsidianWriter(tmp_vault)
    reader = ObsidianReader(tmp_vault)

    note = MemoryNote(
        slug="test-decision-001",
        title="Decisão de Teste",
        type=MemoryType.DECISION,
        project_id="test-proj",
        tags=["decision", "test"],
        content="Esta é uma decisão de teste.\n\nDetalhe adicional aqui.",
        summary="Decisão de teste resumida",
    )

    path = await writer.write(note)
    assert path.exists()
    assert path.suffix == ".md"

    read_note = await reader.read("test-decision-001")
    assert read_note is not None
    assert read_note.title == "Decisão de Teste"
    assert "test" in read_note.tags


@pytest.mark.asyncio
async def test_list_notes(tmp_vault):
    writer = ObsidianWriter(tmp_vault)
    reader = ObsidianReader(tmp_vault)

    for i in range(3):
        note = MemoryNote(
            slug=f"note-{i:03d}",
            title=f"Note {i}",
            type=MemoryType.PROJECT,
            project_id="test-proj",
            tags=["test"],
            content=f"Content {i}",
            summary=f"Summary {i}",
        )
        await writer.write(note)

    notes = await reader.list_notes(project_id="test-proj", note_type=MemoryType.PROJECT)
    assert len(notes) == 3


@pytest.mark.asyncio
async def test_memory_manager_save_decision(tmp_vault):
    from src.memory.memory_manager import MemoryManager
    manager = MemoryManager(tmp_vault)

    record = DecisionRecord(
        decision_id="ADR-001",
        project_id="test-proj",
        title="Usar FastAPI",
        decision="FastAPI como framework principal",
        rationale="Performance e ergonomia",
        context="Precisamos de uma API async",
        made_by="engineer",
    )

    path = await manager.save_decision(record)
    assert path.exists()

    note = await manager.get_note("adr-001")
    assert note is not None
    assert "ADR-001" in note.title


def test_compressor_truncate():
    long_text = "palavra " * 200
    result = ContextCompressor.truncate(long_text, max_tokens=50)
    assert len(result) <= 50 * 4 + 20  # +20 para o " [truncado]"
    assert "[truncado]" in result


def test_compressor_summarize_conversation():
    messages = [
        {"role": "user", "content": f"Mensagem {i}"}
        for i in range(10)
    ]
    summary, recent = ContextCompressor.summarize_conversation(messages, keep_last_n=3)
    assert len(recent) == 3
    assert "Histórico Resumido" in summary


def test_compressor_extract_decisions():
    text = """
    Decidimos usar FastAPI como framework principal.
    Decisão: Migrar para PostgreSQL no lugar de SQLite.
    Optamos por Redis para cache de sessões.
    """
    decisions = ContextCompressor.extract_key_decisions(text)
    assert len(decisions) >= 1
