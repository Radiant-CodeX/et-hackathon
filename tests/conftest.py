"""Shared pytest fixtures for both unit and E2E tests."""
import os
import sys

# Ensure backend is on the path regardless of how pytest is invoked
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Default to stubs so no live services are needed
os.environ.setdefault("USE_STUBS", "true")

import pytest


FIXTURE_ENTITIES_JSON = (
    '{"entities": ['
    '{"name": "Pump-01", "type": "Equipment", "metadata": {"location": "Bay 3"}},'
    '{"name": "Bearing wear", "type": "FailureMode", "metadata": {"severity": "high"}},'
    '{"name": "SKF", "type": "Supplier", "metadata": {}}'
    '], "relationships": ['
    '{"source": "Pump-01", "target": "Bearing wear", "type": "HAS_FAILURE_MODE"},'
    '{"source": "Pump-01", "target": "SKF", "type": "SUPPLIED_BY"}'
    ']}'
)


@pytest.fixture
def mock_llm(monkeypatch):
    """Replace get_chat_response with a canned JSON extraction result."""
    monkeypatch.setattr(
        "ingest.get_chat_response",
        lambda system, user, **kw: FIXTURE_ENTITIES_JSON,
    )


@pytest.fixture
def mock_graph_write(monkeypatch):
    """Swallow graph.write_entities so unit tests don't need Neo4j."""
    monkeypatch.setattr("ingest.graph.write_entities", lambda data: None)


@pytest.fixture
def sample_txt_doc() -> bytes:
    return b"Pump-01 had a bearing failure. Supplier SKF provided the bearing part #6309."


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Minimal valid PDF bytes (empty page) for testing _extract_text."""
    return (
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f\n"
        b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n9\n%%EOF"
    )
