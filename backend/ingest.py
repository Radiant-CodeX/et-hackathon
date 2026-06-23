"""
Ingestion pipeline (Person A).

Parses an uploaded document, extracts entities + relationships via the
shared Azure-backed model, and writes them into the graph.
"""
import io
import json
import uuid

from ai_client import get_chat_response
import graph

SYSTEM = (
    "You extract structured industrial entities from plant documents. "
    "Respond with valid JSON only, no prose."
)


def _extract_text(filename: str, raw: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(raw)) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception:
            return ""
    # txt / md / csv
    return raw.decode("utf-8", errors="ignore")


def _parse_json(text: str) -> dict:
    """Tolerant JSON parse — strips markdown fences if the model adds them."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    try:
        data = json.loads(cleaned)
    except Exception:
        return {"entities": [], "relationships": []}
    data.setdefault("entities", [])
    data.setdefault("relationships", [])
    return data


def extract_entities(text: str) -> dict:
    user = (
        "Extract industrial entities from this document. Return ONLY JSON: "
        '{"entities": [{"name": str, "type": str, "metadata": {}}], '
        '"relationships": [{"source": str, "target": str, "type": str}]}. '
        "Entity types: Equipment, Procedure, FailureMode, Supplier, "
        "ComplianceStd. Relationship types: HAS_FAILURE_MODE, REFERENCES, "
        "CAUSED_BY, SUPPLIED_BY, GOVERNED_BY.\n\nDocument:\n" + text[:4000]
    )
    try:
        raw = get_chat_response(SYSTEM, user, json_mode=True)
        return _parse_json(raw)
    except Exception:
        return {"entities": [], "relationships": []}


def ingest_document(filename: str, raw: bytes) -> dict:
    text = _extract_text(filename, raw)
    data = extract_entities(text)
    try:
        graph.write_entities(data)
    except Exception as exc:
        print(f"[ingest] graph write skipped ({exc})")
    return {
        "status": "ingested",
        "doc_id": str(uuid.uuid4()),
        "entity_count": len(data.get("entities", [])),
    }
