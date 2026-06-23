"""Schema validation tests for all agents (Step 1 in TDD)."""
import pytest
from models import Finding, AgentResult


def test_agent_response_has_required_keys():
    """Test that agent responses contain all required top-level keys."""
    response = {
        "summary": "Bearing failure pattern detected in Pump-01",
        "findings": [
            {
                "text": "Three failures were linked to bearing overheating.",
                "confidence": 0.86,
                "citations": ["maintenance_log_01:chunk_2"]
            }
        ],
        "recommendation": "Inspect bearing supplier quality and reduce inspection interval."
    }

    assert "summary" in response
    assert "findings" in response
    assert "recommendation" in response
    assert isinstance(response["findings"], list)
    assert len(response["findings"]) > 0
    assert "confidence" in response["findings"][0]
    assert "citations" in response["findings"][0]


def test_finding_model_validates():
    """Test that Finding Pydantic model validates correctly."""
    finding = Finding(
        text="Multiple bearing failures found in maintenance logs.",
        confidence=0.86,
        citations=["maintenance_log_01:chunk_2"]
    )
    assert finding.text == "Multiple bearing failures found in maintenance logs."
    assert finding.confidence == 0.86
    assert finding.citations == ["maintenance_log_01:chunk_2"]


def test_agent_result_model_validates():
    """Test that AgentResult Pydantic model validates correctly."""
    result = AgentResult(
        summary="Bearing failure pattern detected",
        findings=[
            Finding(
                text="Three failures linked to bearing overheating",
                confidence=0.86,
                citations=["log_01:chunk_2"]
            )
        ],
        recommendation="Review supplier quality and reduce inspection interval."
    )
    assert result.summary == "Bearing failure pattern detected"
    assert len(result.findings) == 1
    assert result.findings[0].confidence == 0.86


def test_confidence_score_within_valid_range():
    """Test that confidence scores are between 0 and 1."""
    for confidence in [0.0, 0.5, 0.86, 1.0]:
        finding = Finding(
            text="Test finding",
            confidence=confidence,
            citations=["test:chunk_1"]
        )
        assert 0.0 <= finding.confidence <= 1.0


def test_empty_findings_allowed():
    """Test that agents can return empty findings when insufficient evidence."""
    result = AgentResult(
        summary="No strong recurring failure pattern found for Pump-99.",
        findings=[],
        recommendation="Continue monitoring."
    )
    assert result.findings == []
    assert len(result.findings) == 0


def test_citations_format():
    """Test that citations follow the expected format doc_id:chunk_id."""
    finding = Finding(
        text="Test finding",
        confidence=0.82,
        citations=["maintenance_log_01:chunk_2", "supplier_01:chunk_4"]
    )
    for citation in finding.citations:
        assert ":" in citation
        parts = citation.split(":")
        assert len(parts) == 2
        assert parts[0]
        assert parts[1]
