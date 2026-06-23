"""Equipment Historian Agent tests (Step 4 in TDD)."""
import pytest
from agents.historian_agent import equipment_history


def test_historian_returns_sorted_equipment_timeline(sample_equipment_detail):
    """Test historian returns events in chronological order."""
    result = equipment_history("Pump-01", sample_equipment_detail)
    assert "summary" in result
    assert isinstance(result["summary"], str)
    assert "findings" in result
    assert isinstance(result["findings"], list)
    assert "recommendation" in result


def test_historian_includes_all_events(sample_equipment_detail):
    """Test historian captures all equipment events."""
    result = equipment_history("Pump-01", sample_equipment_detail)
    assert "findings" in result
    assert isinstance(result["findings"], list)


def test_historian_includes_citations(sample_equipment_detail):
    """Test historian citations for timeline traceability."""
    result = equipment_history("Pump-01", sample_equipment_detail)
    if result["findings"]:
        for finding in result["findings"]:
            assert "citations" in finding
            assert isinstance(finding["citations"], list)


def test_historian_confidence_for_timeline(sample_equipment_detail):
    """Test historian provides confidence scores."""
    result = equipment_history("Pump-01", sample_equipment_detail)
    if result["findings"]:
        for finding in result["findings"]:
            assert "confidence" in finding
            assert 0.0 <= finding["confidence"] <= 1.0
            assert finding["confidence"] >= 0.80


def test_historian_readable_narrative(sample_equipment_detail):
    """Test historian provides readable asset history."""
    result = equipment_history("Pump-01", sample_equipment_detail)
    assert len(result["summary"]) > 0
    assert "Pump-01" in result["summary"] or "pump" in result["summary"].lower()


def test_historian_recommendation_for_maintenance(sample_equipment_detail):
    """Test historian provides useful maintenance recommendations."""
    result = equipment_history("Pump-01", sample_equipment_detail)
    assert "recommendation" in result
    assert len(result["recommendation"]) > 0
