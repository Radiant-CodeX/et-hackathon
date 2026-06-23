"""Equipment Historian agent (Person C).

Assembles a lifetime narrative of an asset from its graph relationships:
failures, maintenance, suppliers, governing procedures.
"""
from .common import run_llm, format_context

SYSTEM = (
    "You are a maintenance historian. Your task is to build a complete "
    "chronological narrative of an equipment asset from its records.\n"
    "CRITICAL RULES:\n"
    "1. Events must be presented in chronological order\n"
    "2. Every timeline event must be cited with a document reference\n"
    "3. Include commissioning date, major maintenance, failures, and governance\n"
    "4. Confidence should be 0.80+ for documented events\n"
    "5. If no historical data exists, acknowledge insufficient records\n\n"
    "Return ONLY valid JSON: "
    '{"summary": str, "findings": [{"text": str, "confidence": float, "citations": [str]}], "recommendation": str}'
)


def equipment_history(entity_id: str, detail: dict) -> dict:
    """Build a lifetime narrative of equipment asset.

    Args:
        entity_id: The equipment identifier
        detail: Context dict with entity, backlinks, and related data

    Returns:
        Dict with chronological summary, timeline events with citations, and recommendations
    """
    entity = detail.get("entity", {})
    backlinks = detail.get("backlinks", [])
    related = detail.get("related", [])

    # Categorize events by type
    events = {
        "commissioning": [],
        "maintenance": [],
        "failures": [],
        "suppliers": [],
        "procedures": []
    }

    for link in backlinks:
        link_type = link.get("type", "").lower()
        source_name = link.get("source_name", "")

        if "commission" in link_type:
            events["commissioning"].append(link)
        elif "maintain" in link_type or "service" in link_type:
            events["maintenance"].append(link)
        elif "fail" in link_type:
            events["failures"].append(link)
        elif "govern" in link_type or "procedure" in link_type:
            events["procedures"].append(link)

    for rel in related:
        if rel.get("type") == "Supplier":
            events["suppliers"].append(rel)

    # Prepare context for LLM
    context = format_context(detail)
    prompt = f"{SYSTEM}\n\nAsset records:\n{context}"

    # Try to get LLM response with agent identification
    result = run_llm(prompt, agent_name=f"Historian Agent - {entity_id}")
    if result and result.get("summary"):
        return result

    # Deterministic fallback: build timeline from available events
    findings = []

    # Add commissioning event if available
    if events["commissioning"]:
        findings.append({
            "text": f"{entity_id} commissioned.",
            "confidence": 0.90,
            "citations": ["asset_records:commissioning"]
        })

    # Add maintenance history
    if events["maintenance"]:
        findings.append({
            "text": f"{len(events['maintenance'])} maintenance event(s) recorded.",
            "confidence": 0.85,
            "citations": ["maintenance_logs:history"]
        })

    # Add failure history
    if events["failures"]:
        findings.append({
            "text": f"{len(events['failures'])} failure event(s) documented.",
            "confidence": 0.88,
            "citations": ["failure_records:analysis"]
        })

    # Add supplier information
    if events["suppliers"]:
        supplier_names = ", ".join([s.get("name", "Unknown") for s in events["suppliers"]])
        findings.append({
            "text": f"Associated with supplier(s): {supplier_names}.",
            "confidence": 0.92,
            "citations": ["supplier_records:analysis"]
        })

    # Build summary
    if findings:
        event_count = sum(len(v) for v in events.values())
        summary = (
            f"{entity_id} timeline: {event_count} total records including "
            f"commissioning, maintenance, failures, and supplier relationships."
        )
    else:
        summary = f"Insufficient historical records available for {entity_id}. "

    # Recommendation
    if len(events["failures"]) >= 2:
        recommendation = (
            f"This asset shows recurring issues. Recommend predictive maintenance "
            f"and supplier quality review."
        )
    else:
        recommendation = (
            f"Continue standard monitoring. Conduct periodic asset review based on maintenance history."
        )

    return {
        "summary": summary,
        "findings": findings,
        "recommendation": recommendation,
    }
