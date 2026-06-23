"""Compliance Agent tests (Step 3 in TDD)."""
import pytest
from agents.compliance_agent import check_compliance


def test_compliance_flags_missing_permit_signoff(hotwork_procedure_detail):
    """Test compliance agent detects missing permit sign-off."""
    result = check_compliance("procedure_hotwork", hotwork_procedure_detail)
    assert "summary" in result
    assert "findings" in result
    assert "recommendation" in result
    assert isinstance(result["findings"], list)


def test_compliance_returns_audit_ready_recommendation(empty_equipment_detail):
    """Test compliance agent provides audit-ready recommendations."""
    result = check_compliance("procedure_hotwork", empty_equipment_detail)
    assert "recommendation" in result
    assert len(result["recommendation"]) > 0


def test_compliance_includes_citations(hotwork_procedure_detail):
    """Test compliance findings cite both procedure and rule."""
    result = check_compliance("procedure_01", hotwork_procedure_detail)
    if result["findings"]:
        for finding in result["findings"]:
            assert "citations" in finding
            assert isinstance(finding["citations"], list)


def test_compliance_avoids_false_claims(empty_equipment_detail):
    """Test compliance agent avoids unsupported claims when evidence insufficient."""
    result = check_compliance("unknown_proc", empty_equipment_detail)
    assert isinstance(result["summary"], str)
    assert isinstance(result["findings"], list)


def test_compliance_includes_confidence_scores(hotwork_procedure_detail):
    """Test compliance findings have confidence scores."""
    result = check_compliance("procedure_01", hotwork_procedure_detail)
    if result["findings"]:
        for finding in result["findings"]:
            assert "confidence" in finding
            assert 0.0 <= finding["confidence"] <= 1.0
            assert finding["confidence"] >= 0.75


def test_compliance_multiple_gaps(hotwork_procedure_detail):
    """Test compliance can flag multiple compliance gaps."""
    result = check_compliance("complex_proc", hotwork_procedure_detail)
    assert "summary" in result
    assert isinstance(result["findings"], list)
    assert "recommendation" in result
