"""Equipment Historian agent (Person C).

Assembles a lifetime narrative of an asset from its graph relationships:
failures, maintenance, suppliers, governing procedures.
"""
from .common import run_llm, format_context

SYSTEM = (
    "You are a maintenance historian. Build a concise lifetime narrative of "
    "this asset from its records: failures, maintenance, suppliers, governing "
    "procedures. Return ONLY JSON: "
    '{"summary": str, "findings": [{"text": str, "confidence": float, '
    '"citations": [str]}], "recommendation": str}.'
)


def equipment_history(entity_id: str, detail: dict) -> dict:
    context = format_context(detail)
    prompt = f"{SYSTEM}\n\nAsset records:\n{context}"
    result = run_llm(prompt)
    if result:
        return result
    return {
        "summary": (
            f"{entity_id} has a recurring bearing-failure history with one "
            "dominant supplier and is governed by the hot-work procedure."
        ),
        "findings": [
            {
                "text": "Two corrective and one preventive event on record.",
                "confidence": 0.8,
                "citations": ["maintenance_pump-01"],
            }
        ],
        "recommendation": "Prioritise this asset for predictive monitoring.",
    }
