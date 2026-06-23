# Person A — Backend Core (Team Lead) Guide

> Role: Backend Lead | Owns: `backend/` (except `backend/agents/`), API contract, Neo4j schema, `ARCHITECTURE.md`

---

## Your Role in One Line

You are the load-bearing wall. Every other person plugs into your endpoints. If your stubs are up by Hour 6, the team runs in parallel. If they aren't, B and C are blocked.

---

## Step-by-Step Task Checklist

### Phase 1 — Setup (Hours 0–6)

- [ ] **Hour 0–2: Lock the API contract**
  - Run the all-hands kickoff
  - Set up GitHub branches: `feature/backend`, `feature/frontend`, `feature/agents`, `feature/ops`
  - Commit `docs/API_CONTRACT.md` and `docs/ENTITY_SCHEMA.md` (Section 5 of playbook)
  - **This is your single most important task** — B and C are blocked until this is done

- [ ] **Hour 2–6: Scaffold + ship stubs**
  - FastAPI app boots (`main.py`) ✅ already done
  - Neo4j connection wired (`graph.py`) ✅ already done
  - `ai_client.py` shared Azure client written ✅ already done
  - Every route returns a **hardcoded stub response** — verify each one manually with `curl` or Swagger UI at `http://localhost:8000/docs`
  - Run: `uvicorn main:app --reload` and confirm `/health` returns 200

### Phase 2 — Build (Hours 6–30)

- [ ] **Hours 6–18: Ingestion + extraction + graph writes**
  - PDF parsing via `pdfplumber` (`ingest.py`) ✅ scaffold done
  - Entity extraction prompt → Azure AI Foundry → parse JSON (`extract_entities`) ✅ scaffold done
  - `write_entities` writes nodes + relationships to Neo4j ✅ scaffold done
  - **Test with 2–3 of Person D's demo docs** — confirm entities appear in Neo4j browser (`http://localhost:7474`)
  - Add `_parse_json` hardening: handle empty text, model timeouts, malformed JSON ✅ already done

- [ ] **Hours 18–30: Query layer + agent helper functions**
  - `GET /entities` — paginated list ✅ done
  - `GET /entities/{id}` — entity detail + backlinks + related ✅ done
  - `GET /graph/relationships` — full graph for Cytoscape ✅ done
  - `GET /search?q=` — full-text search ✅ done
  - `equipment_context(entity_id)` — bundle for agents ✅ done
  - Add: `get_equipment_history(entity_id)` — returns timeline of related FailureModes + dates
  - Add: `get_similar_failures(entity_id)` — finds other Equipment with same FailureMode
  - Add: `get_supplier_timeline(supplier_id)` — groups failures by supplier

### Phase 3 — Harden (Hours 30–42)

- [ ] Validate extraction accuracy on Person D's 10+ demo docs — target **>85% precision/recall**
- [ ] Add Neo4j full-text index for faster search (see `init_schema`)
- [ ] Handle edge cases: corrupt PDF bytes, empty text pages, model returning 429/5xx
- [ ] Fix any bugs surfaced by Person D's E2E test suite (`tests/test_e2e.py`)
- [ ] Confirm `/graph/relationships` renders 50 nodes in the browser in **under 1 second**

### Phase 4 — Document (Hours 42–48)

- [ ] Write `ARCHITECTURE.md` — data-flow diagram, component boundaries, tech-choice rationale
- [ ] Write `docs/API_REFERENCE.md` — every endpoint with example request/response
- [ ] Write `docs/ENTITY_SCHEMA.md` — 5 node types, 5 relationship types, field definitions
- [ ] **Demo day**: drive the architecture Q&A + run the backend live

---

## Code Structure

```
backend/
├── main.py              # FastAPI app, route definitions, CORS
├── models.py            # Pydantic schemas (API contract — locked at Hour 2)
├── config.py            # Env var loading, feature flags (USE_STUBS)
├── ai_client.py         # Shared Azure AI Foundry client (A writes, C imports)
├── ingest.py            # PDF parsing → entity extraction → graph write
├── graph.py             # All Neo4j queries (schema init, reads, writes)
├── seed.py              # (Person D) demo data loader
├── agents/              # (Person C owns) — do not modify
│   ├── __init__.py
│   ├── common.py
│   ├── rca_agent.py
│   ├── compliance_agent.py
│   └── historian_agent.py
├── requirements.txt
└── Dockerfile
```

**Ownership rule**: You own every file in `backend/` except `backend/agents/`. Person C owns `agents/`. Coordinate on `main.py`'s `/agents/run` route — it's yours structurally, C fills the logic.

---

## Unit Testable Code — Design Rules

The code is already well-structured. Follow these rules to keep every function testable in isolation:

### 1. Pure functions with injected dependencies

```python
# BAD — hardwired to live Neo4j
def search(q: str):
    with get_driver().session() as s:  # cannot mock
        ...

# GOOD — session injected, pure logic
def search(q: str, session):
    rows = session.run("MATCH (n:Entity) ...", q=q)
    return [dict(r) for r in rows]
```

### 2. `ingest.py` — keep extraction separate from I/O

```python
# These three are independently testable:
def _extract_text(filename: str, raw: bytes) -> str: ...   # no network
def extract_entities(text: str) -> dict: ...               # calls AI (mock in tests)
def ingest_document(filename: str, raw: bytes) -> dict: ...# calls both above
```

In tests, mock `get_chat_response` to return a fixture JSON string — no Azure calls needed.

### 3. `graph.py` — wrap driver access so it can be swapped

```python
# In tests, pass a MagicMock session that returns fixture data
def list_entities(limit: int = 100, session=None):
    s = session or get_driver().session().__enter__()
    ...
```

### 4. `ai_client.py` — the seam to mock

```python
# tests/conftest.py
from unittest.mock import patch

@pytest.fixture
def mock_llm(monkeypatch):
    monkeypatch.setattr(
        "ingest.get_chat_response",
        lambda system, user, **kw: '{"entities": [], "relationships": []}'
    )
```

---

## Unit Tests to Write

Create `tests/unit/` for fast, isolated tests (no network, no Neo4j):

```
tests/
├── unit/
│   ├── test_ingest.py       # _extract_text, extract_entities, _parse_json
│   ├── test_graph_queries.py# list_entities, search, full_graph (mock session)
│   └── test_models.py       # Pydantic validation edge cases
├── test_e2e.py              # Person D owns — full pipeline with live services
└── conftest.py              # Shared fixtures, mock_llm, mock_neo4j_session
```

### `tests/unit/test_ingest.py` (write this first)

```python
import pytest
from unittest.mock import patch
from ingest import _parse_json, _extract_text, extract_entities

def test_parse_json_valid():
    raw = '{"entities": [{"name": "Pump-01", "type": "Equipment", "metadata": {}}], "relationships": []}'
    result = _parse_json(raw)
    assert result["entities"][0]["name"] == "Pump-01"

def test_parse_json_strips_markdown_fences():
    raw = '```json\n{"entities": [], "relationships": []}\n```'
    result = _parse_json(raw)
    assert result["entities"] == []

def test_parse_json_malformed_returns_empty():
    result = _parse_json("not json at all")
    assert result == {"entities": [], "relationships": []}

def test_extract_text_txt():
    raw = b"Pump-01 bearing failure"
    assert "Pump-01" in _extract_text("report.txt", raw)

def test_extract_text_unknown_ext_falls_back_to_utf8():
    raw = "Valve-02".encode("utf-8")
    assert "Valve-02" in _extract_text("report.csv", raw)

@patch("ingest.get_chat_response")
def test_extract_entities_parses_llm_response(mock_llm):
    mock_llm.return_value = '{"entities": [{"name": "Pump-01", "type": "Equipment", "metadata": {}}], "relationships": []}'
    result = extract_entities("Pump-01 was inspected")
    assert len(result["entities"]) == 1
    assert result["entities"][0]["type"] == "Equipment"

@patch("ingest.get_chat_response")
def test_extract_entities_handles_llm_error(mock_llm):
    mock_llm.side_effect = Exception("Azure timeout")
    result = extract_entities("any text")
    assert result == {"entities": [], "relationships": []}
```

### `tests/unit/test_models.py`

```python
import pytest
from pydantic import ValidationError
from models import AgentRequest, AgentResult, Finding

def test_agent_request_valid():
    req = AgentRequest(agent_type="rca", entity_id="Pump-01")
    assert req.agent_type == "rca"

def test_agent_request_optional_context():
    req = AgentRequest(agent_type="compliance", entity_id="Valve-02", context={"key": "val"})
    assert req.context == {"key": "val"}

def test_agent_result_defaults():
    result = AgentResult(summary="test", recommendation="fix it")
    assert result.findings == []

def test_finding_requires_confidence():
    with pytest.raises(ValidationError):
        Finding(text="issue found", citations=[])  # missing confidence
```

---

## Best Practices

### Environment & Config
- All secrets via env vars — never hardcode Azure keys or Neo4j passwords in code
- `config.py` is the single source; every module imports from it
- `.env` is in `.gitignore` — commit `.env.example` with empty values only

### API Design
- All response shapes match `models.py` exactly — B and C build against these types
- Return graceful empty results (`[]`, `{}`) instead of 500s where possible — the UI must stay up
- Never change route signatures or response shapes after Hour 2 without a team sync

### Neo4j
- Always use `MERGE` not `CREATE` for nodes — re-ingesting the same doc must be idempotent
- Index on `id` and `name` (already in `init_schema`) — verify these exist before Hour 12
- Keep Cypher in `graph.py` only — no raw Cypher strings in `main.py` or `ingest.py`

### Azure AI Foundry
- All AI calls go through `ai_client.py` — never import `AzureChatOpenAI` anywhere else
- Use `json_mode=True` for extraction calls — prevents prose wrapping the JSON
- Truncate input to 4000 chars (`text[:4000]`) to avoid token limit errors on large PDFs

### Git
- Branch: `feature/backend` — merge only at checkpoints (Hour 12, Hour 30)
- Commit messages: `feat:`, `fix:`, `chore:` prefix, present tense, one sentence
- Never commit `.env` — double-check with `git status` before every push

---

## Critical Handoffs (Do Not Miss)

| Hour | What you deliver | Who is unblocked |
|------|-----------------|-----------------|
| 2    | API contract + entity schema committed to repo | B and C start building |
| 6    | Every route returns a stub response | B and C develop against stubs |
| 8    | Neo4j schema live, real entities queryable | C tests agents on real data |
| 12   | `/graph/relationships` returns real data | B wires real graph component |
| 18   | `/search`, `/entities/{id}` with backlinks | B completes entity panel |
| 30   | Agent helpers (`equipment_context`, etc.) stable | C tunes prompts on real data |

---

## Quick Reference — Run Commands

```bash
# Start everything
docker-compose up

# Backend only (dev mode with hot reload)
cd backend
uvicorn main:app --reload --port 8000

# Run unit tests (fast, no services needed)
pytest tests/unit/ -v

# Run E2E tests (requires docker-compose up)
pytest tests/test_e2e.py -v

# Check all routes are live
curl http://localhost:8000/health
curl http://localhost:8000/entities
curl "http://localhost:8000/search?q=Pump"
```

---

## Judging Criteria You Own

| Criterion | Weight | What you must deliver |
|-----------|--------|-----------------------|
| Technical excellence | 20% | Clean architecture, passing tests, accurate extraction (>85%) |
| Scalability | 15% (shared with D) | Neo4j indexes, Docker deploy, sub-second graph queries |

**Anticipated judge question**: *"How does entity extraction work?"*
Answer: PDFPlumber parses the document text, which is sent to a GPT-4o deployment on Azure AI Foundry with a structured JSON prompt. The response is parsed into our 5-node-type schema and written to Neo4j using MERGE for idempotency.
