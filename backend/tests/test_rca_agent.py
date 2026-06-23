"""RCA Agent tests (Step 2 in TDD)."""
import pytest
from agents.rca_agent import run_rca


def test_rca_detects_repeated_bearing_failure(sample_equipment_detail):
    """Test RCA detects recurring bearing failure pattern."""
    result = run_rca("Pump-01", sample_equipment_detail)
    assert "summary" in result
    assert "findings" in result
    assert "recommendation" in result
    assert isinstance(result["findings"], list)


def test_rca_no_pattern_returns_insufficient_evidence(empty_equipment_detail):
    """Test RCA handles cases with no clear pattern."""
    result = run_rca("Pump-99", empty_equipment_detail)
    assert "summary" in result
    assert "findings" in result
    assert "recommendation" in result
    assert "no strong" in result["summary"].lower() or \
           "insufficient" in result["summary"].lower()


def test_rca_includes_citations(sample_equipment_detail):
    """Test RCA findings include proper citations."""
    result = run_rca("Pump-01", sample_equipment_detail)
    if result["findings"]:
        for finding in result["findings"]:
            assert "citations" in finding
            assert isinstance(finding["citations"], list)


def test_rca_includes_confidence_scores(sample_equipment_detail):
    """Test RCA findings have confidence scores."""
    result = run_rca("Pump-01", sample_equipment_detail)
    if result["findings"]:
        for finding in result["findings"]:
            assert "confidence" in finding
            assert 0.0 <= finding["confidence"] <= 1.0


def test_rca_recommendation_is_actionable(sample_equipment_detail):
    """Test RCA provides actionable recommendations."""
    result = run_rca("Pump-01", sample_equipment_detail)
    assert "recommendation" in result
    assert len(result["recommendation"]) > 0
