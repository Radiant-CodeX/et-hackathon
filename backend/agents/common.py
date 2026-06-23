"""Shared helpers for all three agents."""
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import config
from ai_client import llm


def parse_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    try:
        return json.loads(cleaned)
    except Exception:
        return {}


def run_llm(prompt: str) -> dict:
    """Invoke the shared model and parse a JSON result, or stub it."""
    if config.USE_STUBS or llm is None:
        return {}
    resp = llm.invoke(prompt)
    return parse_json(resp.content)


def format_context(detail: dict) -> str:
    entity = detail.get("entity", {})
    backlinks = detail.get("backlinks", [])
    related = detail.get("related", [])
    lines = [f"Entity: {entity.get('name')} (type: {entity.get('type')})"]
    if backlinks:
        lines.append("Referenced by:")
        for b in backlinks:
            lines.append(f"  - {b['source_name']} ({b['source_type']}) via {b['type']}")
    if related:
        lines.append("Related entities:")
        for r in related:
            lines.append(f"  - {r['name']} ({r['type']})")
    return "\n".join(lines)
