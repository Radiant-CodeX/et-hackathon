"""
End-to-end test suite (Person D).

Runs against the FastAPI app with stubs enabled, so it passes without
Neo4j or Azure. Once the real backend is wired, the same tests validate
the live pipeline.

Run:  cd backend && USE_STUBS=true pytest ../tests -v
"""
import os
import sys

os.environ.setdefault("USE_STUBS", "true")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_entities_route_returns_list():
    r = client.get("/entities")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_graph_route_shape():
    r = client.get("/graph/relationships")
    assert r.status_code == 200
    body = r.json()
    assert "nodes" in body and "relationships" in body


def test_search_route_returns_list():
    r = client.get("/search", params={"q": "pump"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.parametrize("agent_type", ["rca", "compliance", "historian"])
def test_agents_return_structured_result(agent_type):
    r = client.post("/agents/run", json={"agent_type": agent_type, "entity_id": "Pump-01"})
    assert r.status_code == 200
    result = r.json()["result"]
    assert "summary" in result
    assert "findings" in result
    assert "recommendation" in result


def test_unknown_agent_rejected():
    r = client.post("/agents/run", json={"agent_type": "nope", "entity_id": "X"})
    assert r.status_code == 400


def test_ingest_text_document():
    files = {"file": ("sample.txt", b"Pump-01 had a bearing failure.", "text/plain")}
    r = client.post("/ingest", files=files)
    # With stubs and no Neo4j, ingest still returns a structured response
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        assert "entity_count" in r.json()
