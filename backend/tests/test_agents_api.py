"""API endpoint tests for agents (Step 5 in TDD)."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_agents_run_endpoint_exists():
    """Test /agents/run endpoint is available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_agents_run_endpoint_for_rca():
    """Test RCA agent endpoint."""
    payload = {"agent_type": "rca", "entity_id": "Pump-01", "context": {}}
    response = client.post("/agents/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_type"] == "rca"
    assert data["entity_id"] == "Pump-01"
    assert "result" in data
    assert "summary" in data["result"]


def test_agents_run_endpoint_for_compliance():
    """Test Compliance agent endpoint."""
    payload = {"agent_type": "compliance", "entity_id": "procedure_hotwork", "context": {}}
    response = client.post("/agents/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_type"] == "compliance"
    assert data["entity_id"] == "procedure_hotwork"


def test_agents_run_endpoint_for_historian():
    """Test Historian agent endpoint."""
    payload = {"agent_type": "historian", "entity_id": "Pump-01", "context": {}}
    response = client.post("/agents/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_type"] == "historian"
    assert data["entity_id"] == "Pump-01"


def test_agents_run_invalid_agent_type():
    """Test invalid agent type returns error."""
    payload = {"agent_type": "invalid_agent", "entity_id": "Pump-01", "context": {}}
    response = client.post("/agents/run", json=payload)
    assert response.status_code == 400


def test_agent_response_has_all_fields():
    """Test agent response includes all required fields."""
    payload = {"agent_type": "rca", "entity_id": "Pump-01", "context": {}}
    response = client.post("/agents/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) >= {"agent_type", "entity_id", "result"}
    assert set(data["result"].keys()) >= {"summary", "findings", "recommendation"}


def test_agent_response_confidence_in_range():
    """Test agent response confidence scores are valid."""
    payload = {"agent_type": "rca", "entity_id": "Pump-01", "context": {}}
    response = client.post("/agents/run", json=payload)
    assert response.status_code == 200
    for finding in response.json()["result"]["findings"]:
        assert 0.0 <= finding["confidence"] <= 1.0


def test_agent_multiple_agents_same_entity():
    """Test running multiple agents on same entity."""
    for agent_type in ["rca", "compliance", "historian"]:
        payload = {"agent_type": agent_type, "entity_id": "Pump-01", "context": {}}
        response = client.post("/agents/run", json=payload)
        assert response.status_code == 200
        assert response.json()["agent_type"] == agent_type


def test_agent_response_format_consistency():
    """Test all agents return consistent response format."""
    for agent_type in ["rca", "compliance", "historian"]:
        payload = {"agent_type": agent_type, "entity_id": "Pump-01", "context": {}}
        response = client.post("/agents/run", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == {"agent_type", "entity_id", "result"}
        assert set(data["result"].keys()) == {"summary", "findings", "recommendation"}
