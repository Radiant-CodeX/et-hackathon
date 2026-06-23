"""
Test agents with demo data and enhanced LangSmith logging with agent identification.
Shows which agent (RCA, Compliance, Historian) is being called in LangSmith.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable LangSmith tracing with project name
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

from agents.rca_agent import run_rca
from agents.compliance_agent import check_compliance
from agents.historian_agent import equipment_history

# Demo data
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
            "text": "Procedure governs hot work permits. Steps: 1) Requestor completes form 2) Area inspected 3) Gas test performed 4) Fire watch assigned 5) Work proceeds. Note: Does NOT include manager sign-off checkpoint.",
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


def print_header(agent_name, agent_type, entity_id):
    """Print formatted header for agent test."""
    print("\n" + "=" * 80)
    print(f"AGENT: {agent_name}")
    print(f"TYPE: {agent_type}")
    print(f"ENTITY: {entity_id}")
    print(f"LangSmith Project: {os.getenv('LANGCHAIN_PROJECT', 'eth')}")
    print("=" * 80)


def print_result(result):
    """Print formatted result."""
    print("\nSummary:")
    print(f"  {result['summary']}")

    print("\nFindings:")
    if result['findings']:
        for i, finding in enumerate(result['findings'], 1):
            print(f"  [{i}] {finding['text']}")
            print(f"      Confidence: {finding['confidence']:.0%}")
            print(f"      Citations: {', '.join(finding['citations'])}")
    else:
        print("  (No findings)")

    print("\nRecommendation:")
    print(f"  {result['recommendation']}")


def test_rca_agent():
    """Test RCA Agent - Root Cause Analysis."""
    agent_name = "RCA Agent"
    agent_type = "Root Cause Analysis"
    entity_id = "Pump-01"

    print_header(agent_name, agent_type, entity_id)

    result = run_rca(entity_id, PUMP_01_CONTEXT)
    print_result(result)

    return result


def test_compliance_agent():
    """Test Compliance Agent - Regulatory Checking."""
    agent_name = "Compliance Agent"
    agent_type = "Regulatory Compliance"
    entity_id = "HWP-002"

    print_header(agent_name, agent_type, entity_id)

    result = check_compliance(entity_id, HOTWORK_CONTEXT)
    print_result(result)

    return result


def test_historian_agent():
    """Test Historian Agent - Equipment Timeline."""
    agent_name = "Historian Agent"
    agent_type = "Equipment Timeline"
    entity_id = "Pump-01"

    print_header(agent_name, agent_type, entity_id)

    result = equipment_history(entity_id, PUMP_TIMELINE_CONTEXT)
    print_result(result)

    return result


def main():
    """Run all agent tests with demo data and LangSmith tracing."""
    print("\n")
    print("*" * 80)
    print("*  AGENTIC INTELLIGENCE LAYER - DEMO TEST WITH LANGSMITH")
    print("*  Three agents running with demo data + enhanced LangSmith tracing")
    print("*" * 80)

    try:
        # Run all three agents
        print("\n[1/3] Starting RCA Agent...")
        rca_result = test_rca_agent()

        print("\n[2/3] Starting Compliance Agent...")
        compliance_result = test_compliance_agent()

        print("\n[3/3] Starting Historian Agent...")
        historian_result = test_historian_agent()

        # Summary
        print("\n" + "=" * 80)
        print("SUCCESS: All agents executed!")
        print("=" * 80)
        print("\nNext: Check LangSmith dashboard for agent traces")
        print("-" * 80)
        print(f"URL: https://smith.langchain.com")
        print(f"Project: {os.getenv('LANGCHAIN_PROJECT', 'eth')}")
        print("\nYou should see 3 separate runs:")
        print("  [1] RCA Agent - Pump-01 (Root Cause Analysis)")
        print("  [2] Compliance Agent - HWP-002 (Regulatory Compliance)")
        print("  [3] Historian Agent - Pump-01 (Equipment Timeline)")
        print("\nEach run shows:")
        print("  - Agent type and entity being analyzed")
        print("  - LLM system prompts")
        print("  - Azure OpenAI API calls")
        print("  - Tokens used and latency")
        print("  - Full reasoning trace")
        print("=" * 80 + "\n")

        return 0

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
