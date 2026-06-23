"""Root Cause Analysis agent (Person C).

Correlates an entity's failure modes, suppliers, and backlinks to surface
the most likely root cause of recurring failures.
"""
from .common import run_llm, format_context


SYSTEM = (
    "You are a reliability engineer doing root cause analysis on industrial "
    "equipment. Your task is to identify the most likely root cause of recurring "
    "failures by analyzing failure patterns, equipment history, and supplier data. "
    "CRITICAL RULES:\n"
    "1. Only claim a root cause if you have at least 2 failure records\n"
    "2. Every finding MUST cite specific records from the equipment history\n"
    "3. Include confidence scores (0.0-1.0) for each finding\n"
    "4. If insufficient evidence exists, return 'No strong recurring pattern' and empty findings\n"
    "5. Always cite the specific maintenance log entries or supplier records\n\n"
    "Return ONLY valid JSON: "
    '{"summary": str, "findings": [{"text": str, "confidence": float, "citations": [str]}], "recommendation": str}'
)


def run_rca(entity_id: str, detail: dict) -> dict:
    """Analyze root causes of recurring equipment failures.

    Args:
        entity_id: The equipment identifier
        detail: Context dict with entity, backlinks, and related data

    Returns:
        Dict with summary, findings (with confidence/citations), and recommendation
    """
    # Analyze failure patterns from backlinks
    backlinks = detail.get("backlinks", [])
    failure_modes = {}

    for link in backlinks:
        if link.get("type") == "FAILED_WITH":
            failure_mode = link.get("source_name", "Unknown")
            failure_modes[failure_mode] = failure_modes.get(failure_mode, 0) + 1

    # Count related suppliers
    related = detail.get("related", [])
    supplier_count = sum(1 for r in related if r.get("type") == "Supplier")

    # Prepare context for LLM
    context = format_context(detail)
    prompt = f"{SYSTEM}\n\nEquipment history:\n{context}"

    # Try to get LLM response with agent identification
    result = run_llm(prompt, agent_name=f"RCA Agent - {entity_id}")
    if result and result.get("summary"):
        return result

    # Deterministic fallback based on pattern analysis
    if len(failure_modes) >= 2:
        dominant_failure = max(failure_modes, key=failure_modes.get)
        count = failure_modes[dominant_failure]

        return {
            "summary": (
                f"Recurring failure pattern detected for {entity_id}: {dominant_failure} "
                f"appears in {count} separate failure records."
            ),
            "findings": [
                {
                    "text": f"{dominant_failure} identified as recurring across maintenance records.",
                    "confidence": min(0.95, 0.75 + (count * 0.05)),
                    "citations": ["maintenance_logs:root_cause_analysis"],
                },
                {
                    "text": f"Pattern involves {supplier_count} supplier(s) in the equipment ecosystem.",
                    "confidence": 0.70 if supplier_count > 0 else 0.60,
                    "citations": ["supplier_records:analysis"],
                }
            ],
            "recommendation": (
                f"Review procurement and maintenance procedures for {dominant_failure}. "
                f"Consider supplier quality audit and reduce inspection intervals."
            ),
        }

    # No clear pattern
    return {
        "summary": f"No strong recurring failure pattern found for {entity_id}.",
        "findings": [],
        "recommendation": "Continue monitoring. Insufficient failure data to identify pattern.",
    }
