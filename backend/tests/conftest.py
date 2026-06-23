"""Pytest configuration and shared fixtures."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import MagicMock, patch


SAMPLE_EQUIPMENT = {
    "entity": {
        "id": "pump_01",
        "name": "Pump-01",
        "type": "Equipment",
        "metadata": {"location": "Bay 3"}
    },
    "backlinks": [
        {
            "type": "FAILED_WITH",
            "source_id": "failure_01",
            "source_name": "Bearing Failure",
            "source_type": "FailureMode"
        },
        {
            "type": "MAINTAINED_BY",
            "source_id": "maint_01",
            "source_name": "Maintenance Log",
            "source_type": "MaintenanceRecord"
        }
    ],
    "related": [
        {
            "id": "supplier_skf",
            "name": "SKF Industrial",
            "type": "Supplier"
        }
    ]
}

SAMPLE_PROCEDURE = {
    "entity": {
        "id": "procedure_hotwork",
        "name": "Hot Work Procedure",
        "type": "Procedure",
        "metadata": {
            "text": "Hot work completed near Pump-01. Fire watch assigned."
        }
    },
    "backlinks": [
        {
            "type": "GOVERNS",
            "source_id": "pump_01",
            "source_name": "Pump-01",
            "source_type": "Equipment"
        }
    ],
    "related": [
        {
            "id": "oisd_rule",
            "name": "OISD Hot Work Rule",
            "type": "ComplianceStd"
        }
    ]
}

EMPTY_DETAIL = {
    "entity": {
        "id": "equipment_unknown",
        "name": "Equipment-Unknown",
        "type": "Equipment"
    },
    "backlinks": [],
    "related": []
}


@pytest.fixture
def sample_equipment_detail():
    """Sample equipment context for testing."""
    return SAMPLE_EQUIPMENT


@pytest.fixture
def empty_equipment_detail():
    """Empty equipment context for testing insufficient evidence."""
    return EMPTY_DETAIL


@pytest.fixture
def hotwork_procedure_detail():
    """Sample hot work procedure for compliance testing."""
    return SAMPLE_PROCEDURE


@pytest.fixture(autouse=True)
def mock_graph_context(monkeypatch):
    """Auto-mock graph.equipment_context for API tests."""
    try:
        import graph
        def context_side_effect(entity_id):
            if "procedure" in str(entity_id).lower():
                return SAMPLE_PROCEDURE
            return SAMPLE_EQUIPMENT
        monkeypatch.setattr(graph, "equipment_context", context_side_effect)
    except ImportError:
        pass
