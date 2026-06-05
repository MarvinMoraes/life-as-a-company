"""Smoke tests dos schemas Pydantic."""

import pytest
from datetime import datetime

from src.schemas.project import ProjectBrief, PRD, TechnicalPlan, MarketingPlan, Priority, ProjectStatus
from src.schemas.task import TaskBrief, QAEvaluation, AgentRole, QAVerdict, QAFinding
from src.schemas.agent import AgentContextPack, AgentResponse, ContextLayer, ExecutionSnapshot
from src.schemas.memory import MemoryNote, DecisionRecord, MemoryType


def test_project_brief_creation():
    brief = ProjectBrief(
        id="test-project",
        name="Test Project",
        raw_idea="Uma ideia de teste",
        priority=Priority.HIGH,
    )
    assert brief.id == "test-project"
    assert brief.status == ProjectStatus.IDEATION
    assert brief.priority == Priority.HIGH


def test_prd_creation():
    prd = PRD(
        project_id="test-project",
        title="Test PRD",
        executive_summary="Resumo executivo de teste",
        problem="O problema",
        solution="A solução",
        value_proposition="Proposta de valor",
        features=[{"name": "Feature A", "priority": "must", "acceptance_criteria": ["AC1"]}],
    )
    assert prd.version == "1.0"
    assert not prd.approved
    assert len(prd.features) == 1


def test_task_brief_creation():
    task = TaskBrief(
        task_id="task-001",
        project_id="test-project",
        assigned_to=AgentRole.PRODUCT,
        objective="Fazer X",
        context_summary="Contexto mínimo",
        expected_output_format="JSON",
    )
    assert task.max_response_depth == "medium"
    assert task.assigned_to == AgentRole.PRODUCT


def test_agent_context_pack_budget():
    from src.schemas.task import TaskBrief, AgentRole
    task = TaskBrief(
        task_id="t1",
        project_id="p1",
        assigned_to=AgentRole.ENGINEER,
        objective="objetivo",
        context_summary="contexto",
        expected_output_format="JSON",
    )
    pack = AgentContextPack(pack_id="pack-1", task=task, token_budget=100)

    layer_small = ContextLayer(layer_name="task", content="pequeno", token_estimate=50, source="test")
    layer_big = ContextLayer(layer_name="project", content="grande" * 100, token_estimate=200, source="test")

    assert pack.add_layer(layer_small) is True
    assert pack.fits_budget()
    assert pack.add_layer(layer_big) is False  # não cabe


def test_memory_note_frontmatter():
    note = MemoryNote(
        slug="test-note",
        title="Test Note",
        type=MemoryType.DECISION,
        project_id="test-project",
        tags=["tag1", "tag2"],
        content="Conteúdo da nota",
        summary="Resumo",
    )
    fm = note.to_frontmatter_dict()
    assert fm["slug"] == "test-note"
    assert fm["type"] == "decision"
    assert fm["project_id"] == "test-project"


def test_decision_record_markdown():
    record = DecisionRecord(
        decision_id="ADR-001",
        project_id="test-project",
        title="Escolha de Framework",
        decision="Usar FastAPI",
        rationale="Melhor performance async",
        context="Precisamos de uma API REST",
        made_by="engineer",
        alternatives_considered=["Django", "Flask"],
    )
    md = record.to_markdown()
    assert "ADR-001" in md
    assert "FastAPI" in md
    assert "Django" in md


def test_qa_evaluation_creation():
    finding = QAFinding(
        severity="minor",
        category="doc_gap",
        description="Faltou documentar endpoint X",
        recommendation="Adicionar docstring",
    )
    eval_ = QAEvaluation(
        evaluation_id="qa-001",
        project_id="test",
        task_id="task-001",
        artifact_evaluated="PRD v1.0",
        verdict=QAVerdict.APPROVED_WITH_NOTES,
        score=7.5,
        summary="Aprovado com observações menores",
        findings=[finding],
    )
    assert eval_.score == 7.5
    assert eval_.verdict == QAVerdict.APPROVED_WITH_NOTES
    assert len(eval_.findings) == 1
