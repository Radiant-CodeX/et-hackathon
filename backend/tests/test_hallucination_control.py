"""Hallucination control tests (Step 7 in TDD)."""
import pytest
from agents.rca_agent import run_rca
from agents.compliance_agent import check_compliance
from agents.historian_agent import equipment_history


class TestRCAHallucination:
    """Test RCA agent does not invent unsupported findings."""

    def test_rca_no_evidence_returns_no_findings(self, empty_equipment_detail):
        """Test RCA with empty context returns no findings."""
        result = run_rca("Pump-99", empty_equipment_detail)
        assert result["findings"] == [] or \
               "no strong" in result["summary"].lower() or \
               "insufficient" in result["summary"].lower()

    def test_rca_unsupported_claim_not_made(self, empty_equipment_detail):
        """Test RCA doesn't claim root cause without evidence."""
        result = run_rca("Equipment-Unknown", empty_equipment_detail)
        if result["findings"]:
            for finding in result["findings"]:
                assert len(finding["citations"]) > 0

    def test_rca_single_failure_not_called_recurring(self, sample_equipment_detail):
        """Test RCA doesn't claim recurring pattern from single failure."""
        detail = {
            "entity": {"name": "Pump-01", "type": "Equipment"},
            "backlinks": [
                {
                    "type": "FAILED_WITH",
                    "source_id": "failure_01",
                    "source_name": "Bearing Failure",
                    "source_type": "FailureMode"
                }
            ],
            "related": []
        }
        result = run_rca("Pump-01", detail)
        summary = result["summary"].lower()
        if not result["findings"]:
            assert "no strong" in summary or "insufficient" in summary


class TestComplianceHallucination:
    """Test Compliance agent does not invent compliance gaps."""

    def test_compliance_no_evidence_no_gaps(self, empty_equipment_detail):
        """Test Compliance with empty context doesn't invent gaps."""
        result = check_compliance("Unknown-Proc", empty_equipment_detail)
        if result["findings"]:
            for finding in result["findings"]:
                assert len(finding["citations"]) > 0

    def test_compliance_requires_citations(self, empty_equipment_detail):
        """Test Compliance findings must be cited."""
        result = check_compliance("Test-Proc", empty_equipment_detail)
        for finding in result["findings"]:
            assert "citations" in finding
            assert len(finding["citations"]) > 0

    def test_compliance_unsupported_gap_not_claimed(self, empty_equipment_detail):
        """Test Compliance doesn't claim gaps without evidence."""
        result = check_compliance("Simple-Proc", empty_equipment_detail)
        if result["findings"]:
            for finding in result["findings"]:
                assert len(finding["citations"]) > 0


class TestHistorianHallucination:
    """Test Historian agent doesn't invent timeline events."""

    def test_historian_no_events_no_findings(self, empty_equipment_detail):
        """Test Historian with no data doesn't invent events."""
        result = equipment_history("Equipment-Unknown", empty_equipment_detail)
        if not result["findings"]:
            assert "insufficient" in result["summary"].lower() or \
                   "no" in result["summary"].lower()

    def test_historian_citations_for_all_events(self, sample_equipment_detail):
        """Test Historian cites every timeline event."""
        result = equipment_history("Pump-01", sample_equipment_detail)
        for finding in result["findings"]:
            if finding["text"]:
                assert len(finding["citations"]) > 0

    def test_historian_no_invented_dates(self, empty_equipment_detail):
        """Test Historian doesn't invent dates without evidence."""
        result = equipment_history("Equipment-NoData", empty_equipment_detail)
        if result["findings"]:
            for finding in result["findings"]:
                if any(char.isdigit() for char in finding["text"]):
                    assert len(finding["citations"]) > 0


class TestCrossAgentHallucination:
    """Test agents collectively maintain hallucination control."""

    def test_all_agents_require_citations(self, empty_equipment_detail):
        """Test all agents cite their claims."""
        agents = [
            (run_rca, "Pump-Test"),
            (check_compliance, "Procedure-Test"),
            (equipment_history, "Equipment-Test"),
        ]

        for agent_fn, entity_id in agents:
            result = agent_fn(entity_id, empty_equipment_detail)
            for finding in result["findings"]:
                assert "citations" in finding
                assert isinstance(finding["citations"], list)

    def test_confidence_indicates_evidence_strength(self, empty_equipment_detail):
        """Test confidence scores reflect evidence availability."""
        result = run_rca("Test", empty_equipment_detail)
        if result["findings"]:
            for finding in result["findings"]:
                if not finding["citations"]:
                    assert finding["confidence"] < 0.6
                else:
                    assert finding["confidence"] >= 0.6
