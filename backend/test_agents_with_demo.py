"""
Test agents with demo data and LangSmith logging.
Run this to see agent calls in LangSmith dashboard.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

from langchain_core.callbacks import CallbackManager
from langsmith.run_trees import RunTree
from agents.rca_agent import run_rca
from agents.compliance_agent import check_compliance
from agents.historian_agent import equipment_history

# Demo data context
PUMP_01_CONTEXT = {
    "entity": {
        "id": "pump_01",
        "name": "Pump-01",
        "type": "Equipment",
        "metadata": {
            "location": "Bay 3, Cooling Water System",
            "asset_class": "Centrifugal pump"
        }
    },
    "backlinks": [
        {
            "type": "FAILED_WITH",
            "source_id": "failure_bearing_01",
            "source_name": "Bearing Wear - Dec 2024",
            "source_type": "FailureMode"
        },
        {
            "type": "FAILED_WITH",
            "source_id": "failure_bearing_02",
            "source_name": "Bearing Wear - Aug 2024",
            "source_type": "FailureMode"
        },
        {
            "type": "MAINTAINED_BY",
            "source_id": "maintenance_seal_jan2025",
            "source_name": "Seal Replacement - Jan 2025",
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

HOTWORK_CONTEXT = {
    "entity": {
        "id": "procedure_hotwork",
        "name": "Hot Work Permit Procedure",
        "type": "Procedure",
        "metadata": {
            "text": "Procedure governs hot work permits. Steps: 1) Requestor completes form 2) Area inspected 3) Gas test performed 4) Fire watch assigned 5) Work proceeds. Note: Does NOT include manager sign-off checkpoint prior to commencement.",
            "document_id": "HWP-002",
            "revision": "3"
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
            "id": "oisd_105",
            "name": "OISD-105 Work Permit System",
            "type": "ComplianceStd"
        }
    ]
}

PUMP_TIMELINE_CONTEXT = {
    "entity": {
        "id": "pump_01",
        "name": "Pump-01",
        "type": "Equipment",
        "metadata": {
            "location": "Bay 3",
            "asset_class": "Centrifugal pump"
        }
    },
    "backlinks": [
        {
            "type": "COMMISSIONED",
            "source_id": "commissioning_2024",
            "source_name": "Equipment commissioned",
            "source_type": "Event"
        },
        {
            "type": "FAILED_WITH",
            "source_id": "failure_bearing_aug2024",
            "source_name": "Bearing wear - Aug 2024",
            "source_type": "FailureEvent"
        },
        {
            "type": "FAILED_WITH",
            "source_id": "failure_bearing_dec2024",
            "source_name": "Bearing wear - Dec 2024",
            "source_type": "FailureEvent"
        },
        {
            "type": "MAINTAINED_BY",
            "source_id": "maintenance_seal_jan2025",
            "source_name": "Seal replacement - Jan 2025",
            "source_type": "MaintenanceEvent"
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


def test_rca_agent():
    """Test RCA Agent with Pump-01 demo data."""
    print("\n" + "="*70)
    print("Testing RCA Agent (Root Cause Analysis)")
    print("="*70)
    print("LangSmith trace: RCA Agent - Root Cause Analysis for Pump-01")

    result = run_rca("Pump-01", PUMP_01_CONTEXT)

    print("\nSummary:")
    print(f"  {result['summary']}")

    print("\nFindings:")
    for i, finding in enumerate(result['findings'], 1):
        print(f"  {i}. {finding['text']}")
        print(f"     Confidence: {finding['confidence']:.0%}")
        print(f"     Citations: {', '.join(finding['citations'])}")

    print("\nRecommendation:")
    print(f"  {result['recommendation']}")

    return result


def test_compliance_agent():
    """Test Compliance Agent with Hot Work Procedure."""
    print("\n" + "="*70)
    print("Testing Compliance Agent (Regulatory Checking)")
    print("="*70)

    result = check_compliance("HWP-002", HOTWORK_CONTEXT)

    print("\nSummary:")
    print(f"  {result['summary']}")

    print("\nFindings:")
    if result['findings']:
        for i, finding in enumerate(result['findings'], 1):
            print(f"  {i}. {finding['text']}")
            print(f"     Confidence: {finding['confidence']:.0%}")
            print(f"     Citations: {', '.join(finding['citations'])}")
    else:
        print("  No compliance gaps found.")

    print("\nRecommendation:")
    print(f"  {result['recommendation']}")

    return result


def test_historian_agent():
    """Test Historian Agent with Pump-01 timeline."""
    print("\n" + "="*70)
    print("Testing Historian Agent (Equipment Timeline)")
    print("="*70)

    result = equipment_history("Pump-01", PUMP_TIMELINE_CONTEXT)

    print("\nSummary:")
    print(f"  {result['summary']}")

    print("\nTimeline Events:")
    for i, finding in enumerate(result['findings'], 1):
        print(f"  {i}. {finding['text']}")
        print(f"     Confidence: {finding['confidence']:.0%}")
        print(f"     Citations: {', '.join(finding['citations'])}")

    print("\nRecommendation:")
    print(f"  {result['recommendation']}")

    return result


def main():
    """Run all agent tests with demo data."""
    print("\n")
    print("*" * 70)
    print("*  AGENTIC INTELLIGENCE LAYER - DEMO TEST")
    print("*  Testing with demo data + LangSmith tracing enabled")
    print("*" * 70)

    try:
        # Run all three agents
        rca_result = test_rca_agent()
        compliance_result = test_compliance_agent()
        historian_result = test_historian_agent()

        # Summary
        print("\n" + "="*70)
        print("All agents executed successfully!")
        print("="*70)
        print("\nCheck LangSmith dashboard to see traces:")
        print("  https://smith.langchain.com")
        print(f"\nProject: {os.getenv('LANGCHAIN_PROJECT', 'eth')}")
        print("\nYou should see 3 agent runs with full tracing of LLM calls.")
        print("="*70 + "\n")

        return 0

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
