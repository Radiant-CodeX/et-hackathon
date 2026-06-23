"""Unit tests for models.py — pure Pydantic validation, no services."""
import pytest
from pydantic import ValidationError

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from models import (
    EntitySummary, EntityDetail, Backlink,
    GraphNode, GraphRelationship, GraphResponse,
    IngestResponse,
    AgentRequest, AgentResult, Finding, AgentResponse,
)


# ---------- EntitySummary ----------

def test_entity_summary_required_fields():
    e = EntitySummary(id="Pump-01", name="Pump-01", type="Equipment")
    assert e.id == "Pump-01"
    assert e.score is None


def test_entity_summary_with_score():
    e = EntitySummary(id="x", name="x", type="Equipment", score=0.92)
    assert e.score == 0.92


def test_entity_summary_missing_id_raises():
    with pytest.raises(ValidationError):
        EntitySummary(name="Pump-01", type="Equipment")


# ---------- AgentRequest ----------

def test_agent_request_valid_rca():
    req = AgentRequest(agent_type="rca", entity_id="Pump-01")
    assert req.agent_type == "rca"
    assert req.context is None


def test_agent_request_valid_compliance():
    req = AgentRequest(agent_type="compliance", entity_id="Valve-02")
    assert req.entity_id == "Valve-02"


def test_agent_request_with_context():
    req = AgentRequest(agent_type="historian", entity_id="Motor-03", context={"depth": 2})
    assert req.context == {"depth": 2}


def test_agent_request_missing_entity_id_raises():
    with pytest.raises(ValidationError):
        AgentRequest(agent_type="rca")


# ---------- Finding ----------

def test_finding_valid():
    f = Finding(text="Bearing failure detected", confidence=0.86, citations=["doc1:chunk3"])
    assert f.confidence == 0.86


def test_finding_missing_confidence_raises():
    with pytest.raises(ValidationError):
        Finding(text="some finding", citations=[])


def test_finding_default_citations():
    f = Finding(text="issue", confidence=0.5)
    assert f.citations == []


# ---------- AgentResult ----------

def test_agent_result_defaults():
    result = AgentResult(summary="Bearing wear detected")
    assert result.findings == []
    assert result.recommendation == ""


def test_agent_result_with_findings():
    f = Finding(text="SKF bearing failure", confidence=0.91, citations=["maint_log:1"])
    result = AgentResult(summary="Root cause identified", findings=[f], recommendation="Replace bearings")
    assert len(result.findings) == 1
    assert result.recommendation == "Replace bearings"


# ---------- AgentResponse ----------

def test_agent_response_full():
    result = AgentResult(summary="Test")
    resp = AgentResponse(agent_type="rca", entity_id="Pump-01", result=result)
    assert resp.agent_type == "rca"


# ---------- GraphResponse ----------

def test_graph_response_defaults_empty():
    g = GraphResponse()
    assert g.nodes == []
    assert g.relationships == []


def test_graph_response_with_data():
    node = GraphNode(id="Pump-01", name="Pump-01", type="Equipment")
    rel = GraphRelationship(source="Pump-01", target="SKF", type="SUPPLIED_BY")
    g = GraphResponse(nodes=[node], relationships=[rel])
    assert len(g.nodes) == 1
    assert g.relationships[0].type == "SUPPLIED_BY"


# ---------- IngestResponse ----------

def test_ingest_response_valid():
    r = IngestResponse(status="ingested", doc_id="abc-123", entity_count=5)
    assert r.entity_count == 5


def test_ingest_response_missing_doc_id_raises():
    with pytest.raises(ValidationError):
        IngestResponse(status="ingested", entity_count=5)
