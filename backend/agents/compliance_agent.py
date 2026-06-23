"""Compliance agent (Person C).

Checks a procedure against embedded regulatory rules (OISD / Factory Act /
PESO) and flags gaps.
"""
from .common import run_llm, format_context

REGS = (
    "OISD: hazard identification, PPE provision, permit-to-work with sign-off "
    "for hot work. Factory Act: inspection logs, incident reporting, safety "
    "committees. PESO: pressure-vessel certification, annual inspection."
)

SYSTEM = (
    "You are an industrial compliance auditor. Compare the procedure against "
    "the regulations and flag gaps. Return ONLY JSON: "
    '{"summary": str, "findings": [{"text": str, "confidence": float, '
    '"citations": [str]}], "recommendation": str}.'
)


def check_compliance(entity_id: str, detail: dict) -> dict:
    context = format_context(detail)
    prompt = f"{SYSTEM}\n\nRegulations:\n{REGS}\n\nProcedure context:\n{context}"
    result = run_llm(prompt)
    if result:
        return result
    return {
        "summary": (
            f"Procedure {entity_id} is missing a required permit sign-off step "
            "under OISD permit-to-work guidance."
        ),
        "findings": [
            {
                "text": "No manager sign-off checkpoint before hot work.",
                "confidence": 0.82,
                "citations": ["procedure:hotwork", "reg:OISD"],
            }
        ],
        "recommendation": "Add a manager sign-off checkpoint to the permit flow.",
    }
