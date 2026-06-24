"""Root Cause Analysis agent (Person C).

Correlates an entity's failure modes, suppliers, and backlinks to surface
the most likely root cause of recurring failures.
"""
from .common import run_llm, format_context

SYSTEM = (
    "You are a reliability engineer doing root cause analysis on industrial "
    "equipment. Identify the most likely root cause of recurring failures and "
    "cite the specific records you used. Return ONLY JSON: "
    '{"summary": str, "findings": [{"text": str, "confidence": float, '
    '"citations": [str]}], "recommendation": str}.'
)


def run_rca(entity_id: str, detail: dict) -> dict:
    context = format_context(detail)
    prompt = f"{SYSTEM}\n\nEquipment history:\n{context}"
    result = run_llm(prompt)
    if result:
        return result
    # Stub fallback — lets the demo run with no Azure key
    return {
        "summary": (
            f"Recurring failures on {entity_id} trace to bearing wear linked "
            "to a single supplier across multiple incidents."
        ),
        "findings": [
            {
                "text": "Bearing wear appears in 3 separate corrective logs.",
                "confidence": 0.86,
                "citations": ["maintenance_pump-01:rec2"],
            },
            {
                "text": "All three failures used bearings from supplier SKF.",
                "confidence": 0.78,
                "citations": ["maintenance_pump-01:rec2", "supplier:SKF"],
            },
        ],
        "recommendation": "Open a supplier qualification review for SKF bearings.",
    }
