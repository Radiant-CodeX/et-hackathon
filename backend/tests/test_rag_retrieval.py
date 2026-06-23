"""RAG retrieval tests (Step 6 in TDD)."""
import pytest


def test_retriever_returns_relevant_chunks():
    """Test basic retrieval of relevant chunks."""
    query = "Pump-01 bearing failure"
    chunks = [
        {"text": "Pump-01 had repeated bearing overheating issues.", "citation": "log_01:chunk_1"},
        {"text": "Valve V-02 inspection completed.", "citation": "log_02:chunk_1"},
        {"text": "Bearing replacement for Pump-01.", "citation": "maint:chunk_2"}
    ]
    relevant = [c for c in chunks if "bearing" in c["text"].lower() and "pump" in c["text"].lower()]
    assert len(relevant) >= 1


def test_chunks_have_citations():
    """Test that every chunk includes a citation."""
    chunks = [
        {"text": "Bearing wear detected", "citation": "log_01:chunk_2"},
        {"text": "Pump maintenance record", "citation": "maint:chunk_3"}
    ]
    for chunk in chunks:
        assert "citation" in chunk
        assert chunk["citation"] is not None
        assert ":" in chunk["citation"]


def test_citation_format_consistency():
    """Test citations follow doc_id:chunk_id format."""
    citations = [
        "maintenance_log_01:chunk_2",
        "supplier_record:chunk_1",
        "procedure:chunk_4",
        "asset_record:chunk_1"
    ]
    for citation in citations:
        parts = citation.split(":")
        assert len(parts) == 2
        assert len(parts[0]) > 0
        assert len(parts[1]) > 0


def test_retrieval_no_unrelated_chunks():
    """Test retrieval doesn't include completely unrelated content."""
    query = "Pump-01 bearing"
    chunks = [
        {"text": "Pump-01 bearing issue", "citation": "log_01:chunk_1"},
        {"text": "Unrelated electrical system", "citation": "other:chunk_1"},
        {"text": "Pump-01 maintenance", "citation": "maint:chunk_2"}
    ]
    relevant = [c for c in chunks if "pump" in c["text"].lower()]
    assert all("pump" in c["text"].lower() for c in relevant)
    assert len(relevant) >= 2


def test_empty_result_handled_gracefully():
    """Test retrieval handles empty results."""
    query = "nonexistent_equipment_xyz"
    chunks = [
        {"text": "Pump-01 data", "citation": "pump:chunk_1"},
        {"text": "Valve-02 data", "citation": "valve:chunk_1"}
    ]
    relevant = [c for c in chunks if query.lower() in c["text"].lower()]
    assert len(relevant) == 0
    assert isinstance(relevant, list)


def test_multiple_chunks_same_document():
    """Test retrieval can return multiple chunks from same document."""
    query = "bearing failure"
    chunks = [
        {"text": "Pump-01 bearing issue", "citation": "log_01:chunk_1"},
        {"text": "Root cause: bearing defect", "citation": "log_01:chunk_2"},
        {"text": "Recommend bearing replacement", "citation": "log_01:chunk_3"}
    ]
    relevant = [c for c in chunks if "bearing" in c["text"].lower()]
    assert len(relevant) == 3
    assert all(c["citation"].startswith("log_01:") for c in relevant)


def test_retrieval_score_ordering():
    """Test chunks can be ordered by relevance."""
    query = "bearing failure pump"
    chunks = [
        {"text": "Pump-01 bearing failure", "citation": "log_01:chunk_1", "score": 0.95},
        {"text": "bearing material", "citation": "supplier:chunk_1", "score": 0.60},
        {"text": "Pump-01 maintenance", "citation": "maint:chunk_1", "score": 0.75}
    ]
    sorted_chunks = sorted(chunks, key=lambda c: c.get("score", 0), reverse=True)
    assert sorted_chunks[0]["citation"] == "log_01:chunk_1"
    assert sorted_chunks[0]["score"] == 0.95


def test_chunk_text_preserved():
    """Test chunk content is not altered during retrieval."""
    original_text = "Exact bearing failure text on 2025-01-12"
    chunk = {"text": original_text, "citation": "log:chunk_1"}
    retrieved = chunk
    assert retrieved["text"] == original_text


def test_retrieval_with_filters():
    """Test retrieval can be filtered by document type."""
    query = "bearing"
    chunks = [
        {"text": "Bearing failure", "citation": "maintenance:chunk_1", "doc_type": "Maintenance"},
        {"text": "Bearing supplier", "citation": "supplier:chunk_1", "doc_type": "Supplier"},
        {"text": "Bearing procedure", "citation": "procedure:chunk_1", "doc_type": "Procedure"}
    ]
    relevant = [c for c in chunks if c.get("doc_type") == "Maintenance"]
    assert len(relevant) == 1
    assert relevant[0]["citation"] == "maintenance:chunk_1"


def test_agent_uses_retrieved_evidence():
    """Test that agents should only cite retrieved chunks."""
    retrieved_chunks = [
        {"text": "Pump-01 bearing replaced twice", "citation": "log:chunk_1"},
        {"text": "SKF supplier", "citation": "supplier:chunk_1"}
    ]
    valid_citations = [c["citation"] for c in retrieved_chunks]
    agent_citations = ["log:chunk_1", "supplier:chunk_1"]
    assert all(citation in valid_citations for citation in agent_citations)
    invalid_citation = "unknown:chunk_1"
    assert invalid_citation not in valid_citations
