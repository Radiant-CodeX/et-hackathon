# Architecture — Industrial Knowledge Intelligence Platform

## Data Flow (end to end)

```
[ Documents ]                       Person D supplies demo docs
     |
     v
[ Ingestion + Entity Extraction ]   Person A  (backend/ingest.py)
     |   PDFPlumber parses text
     |   Azure AI Foundry (GPT-4o) extracts entities + relationships as JSON
     v
[ Neo4j Knowledge Graph ]           Person A  (backend/graph.py)
     |   Nodes: Equipment, Procedure, FailureMode, Supplier, ComplianceStd
     |   Relationships: HAS_FAILURE_MODE, REFERENCES, CAUSED_BY, SUPPLIED_BY, GOVERNED_BY
     v
[ FastAPI REST Layer ]               Person A owns routes; Person C owns agent logic
     |   POST /ingest
     |   GET  /entities  /entities/{id}  /search
     |   GET  /graph/relationships
     |   POST /agents/run
     |
     +------------------+------------------+
     |                  |                  |
     v                  v                  v
[ React UI ]      [ Agent Layer ]    [ Tests + Demo ]
  Person B          Person C           Person D
  Cytoscape         RCA / Compliance   pytest E2E
  graph explorer    Historian agents   seed script
```

## Component Ownership

| Layer | Technology | Owner | Directory |
|-------|-----------|-------|-----------|
| Document ingestion | PDFPlumber + Azure AI Foundry | Person A | `backend/ingest.py` |
| Knowledge graph | Neo4j 5 | Person A | `backend/graph.py` |
| REST API | FastAPI (Python 3.11) | Person A | `backend/main.py` |
| Shared AI client | LangChain + Azure AI Foundry | Person A | `backend/ai_client.py` |
| Agent orchestration | LangChain agents | Person C | `backend/agents/` |
| Frontend / graph viz | React + Vite + Cytoscape | Person B | `frontend/` |
| Demo data + DevOps | Docker Compose + pytest | Person D | `demo-data/`, `tests/`, `docker-compose.yml` |

## AI Model Layer — Azure AI Foundry

All AI calls go through `backend/ai_client.py`. This file is the single place the Azure LangChain model is configured.

```python
# Person A imports:
from ai_client import get_chat_response   # single-turn helper for extraction

# Person C imports:
from ai_client import llm, embeddings     # LangChain objects for chains + RAG
```

Environment variables (set in `.env` and `docker-compose.yml`):

```
AZURE_INFERENCE_ENDPOINT=https://<resource>.services.ai.azure.com
AZURE_INFERENCE_KEY=<key>
AZURE_DEPLOYMENT_NAME=gpt-4o
AZURE_API_VERSION=2024-10-21
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-3-small
```

Set `USE_STUBS=true` (default) to run the whole app without Azure — all routes return realistic fixture data so B and C can develop locally.

## Stub Mode

The application supports two operating modes:

| `USE_STUBS` | AI calls | Neo4j calls | Use when |
|-------------|----------|-------------|----------|
| `true` (default) | Canned JSON responses | Fixture data in memory | Local development — no services needed |
| `false` | Real Azure GPT-4o | Real Neo4j queries | Integration and demo |

## Why Neo4j over a Vector DB?

Our differentiator is **explicit, queryable relationships** — `Equipment → FailureMode → Supplier`. A graph database makes those traversals first-class. We layer RAG (Chroma + embeddings, used by Person C's agents) on top for free-text retrieval, but the graph is the showcase.

Ready answer for judges: *"The graph gives us structural reasoning — we can ask 'which supplier's components appear in the most failure events?' as a graph traversal, not just a similarity search."*

## Repository Layout

```
et-hackathon/
├── ARCHITECTURE.md          # this file (Person A)
├── README.md                # setup guide (shared)
├── docker-compose.yml       # one-command setup (Person D)
├── .env                     # secrets — never committed
├── .env.example             # empty placeholders — committed
├── backend/
│   ├── main.py              # FastAPI app + all routes (Person A)
│   ├── models.py            # Pydantic API shapes — locked contract
│   ├── config.py            # env var loading
│   ├── ai_client.py         # shared Azure LangChain client (Person A writes, C imports)
│   ├── ingest.py            # PDF parse → entity extraction → graph write
│   ├── graph.py             # all Neo4j queries + stub fixtures
│   ├── seed.py              # demo data loader (Person D drives content)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── agents/              # (Person C owns entirely)
│       ├── rca_agent.py
│       ├── compliance_agent.py
│       └── historian_agent.py
├── frontend/                # React + Vite + Cytoscape (Person B)
├── demo-data/               # 10+ realistic industrial docs (Person D)
├── tests/
│   ├── test_e2e.py          # end-to-end suite (Person D)
│   └── unit/               # unit tests — no services (Person A)
│       ├── test_ingest.py
│       └── test_models.py
├── docs/
│   ├── api_contract.md      # locked API shapes
│   └── ENTITY_SCHEMA.md     # node + relationship types
└── presentation/            # slides + demo video (Person D)
```

## Performance Targets (must-pass checks)

| Metric | Target | Owner |
|--------|--------|-------|
| Graph render (50 nodes) | < 1 second | B + A (Neo4j indexes) |
| Agent response | < 5 seconds | C |
| Entity extraction precision/recall | > 85% | A |
| `pytest tests/` pass rate | ≥ 80% | A + D |
| `docker-compose up` from fresh clone | Zero manual steps | D |
