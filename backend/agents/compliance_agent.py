"""Compliance agent (Person C).

Checks a procedure against embedded regulatory rules (OISD / Factory Act /
PESO) and flags gaps.
"""
from .common import run_llm, format_context

# Regulatory reference library
COMPLIANCE_RULES = {
    "OISD": [
        "hazard identification required",
        "PPE provision mandatory",
        "permit-to-work with supervisor sign-off for hot work",
        "safety checklist completion"
    ],
    "Factory Act": [
        "inspection logs required",
        "incident reporting mandatory",
        "safety committee involvement",
        "worker notification procedures"
    ],
    "PESO": [
        "pressure-vessel certification required",
        "annual inspection mandatory",
        "third-party verification required"
    ]
}

SYSTEM = (
    "You are an industrial compliance auditor. Your task is to compare procedures "
    "against regulatory requirements and identify compliance gaps.\n"
    "CRITICAL RULES:\n"
    "1. Only flag gaps where evidence of non-compliance exists\n"
    "2. Cite both the procedure section AND the regulatory requirement\n"
    "3. Use confidence scores 0.75+ for compliance gaps\n"
    "4. If no compliance rules apply, return empty findings\n"
    "5. Every finding must reference specific procedure and regulation\n\n"
    "Return ONLY valid JSON: "
    '{"summary": str, "findings": [{"text": str, "confidence": float, "citations": [str]}], "recommendation": str}'
)


def check_compliance(entity_id: str, detail: dict) -> dict:
    """Check procedure compliance against regulatory standards.

    Args:
        entity_id: The procedure or equipment identifier
        detail: Context dict with entity, backlinks, and related compliance standards

    Returns:
        Dict with summary, compliance gap findings, and audit recommendations
    """
    entity = detail.get("entity", {})
    entity_text = str(entity.get("metadata", {}).get("text", "")).lower()
    backlinks = detail.get("backlinks", [])
    related = detail.get("related", [])

    # Identify applicable compliance standards
    applicable_standards = {
        r.get("name", ""): r.get("type", "")
        for r in related
        if r.get("type") == "ComplianceStd"
    }

    # Prepare context for LLM
    context = format_context(detail)
    prompt = f"{SYSTEM}\n\nRegulations:\n{_format_regs()}\n\nProcedure context:\n{context}"

    # Try to get LLM response with agent identification
    result = run_llm(prompt, agent_name=f"Compliance Agent - {entity_id}")
    if result and result.get("summary"):
        return result

    # Deterministic fallback: check for common gaps
    findings = []

    # Check for hot work compliance
    if "hot work" in entity_text or "hotwork" in entity_text:
        if "sign-off" not in entity_text and "signoff" not in entity_text:
            findings.append({
                "text": "Missing supervisor sign-off checkpoint for hot work.",
                "confidence": 0.82,
                "citations": [f"procedure:{entity_id}", "regulation:OISD_hotwork"]
            })

    # Check for PPE requirements
    if "hot work" in entity_text and "ppe" not in entity_text:
        findings.append({
            "text": "PPE requirements not explicitly stated in hot work procedure.",
            "confidence": 0.75,
            "citations": [f"procedure:{entity_id}", "regulation:OISD_ppe"]
        })

    # Check for hazard identification
    if any(x in entity_text for x in ["high risk", "hazardous", "danger"]):
        if "hazard" not in entity_text and "risk" not in entity_text:
            findings.append({
                "text": "Hazard identification section missing from procedure.",
                "confidence": 0.80,
                "citations": [f"procedure:{entity_id}", "regulation:OISD_hazard"]
            })

    # Return based on findings
    if findings:
        return {
            "summary": f"Compliance gaps detected in procedure {entity_id}. "
                      f"{len(findings)} required element(s) missing or unclear.",
            "findings": findings,
            "recommendation": "Add missing compliance elements and conduct supervisory review before approval.",
        }

    return {
        "summary": f"Procedure {entity_id} appears compliant with applicable regulations.",
        "findings": [],
        "recommendation": "No immediate compliance gaps identified. Schedule routine audit.",
    }


def _format_regs() -> str:
    """Format regulatory requirements for display."""
    lines = []
    for std, rules in COMPLIANCE_RULES.items():
        lines.append(f"{std}:")
        for rule in rules:
            lines.append(f"  - {rule}")
    return "\n".join(lines)
