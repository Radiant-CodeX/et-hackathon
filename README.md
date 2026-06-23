# Industrial Knowledge Intelligence Platform

ET AI Hackathon 2026 — Problem Statement #8.
An AI platform that ingests heterogeneous industrial documents, builds a
knowledge graph, and runs reasoning agents over it to surface insights no
single engineer could connect alone.

LangChain is the orchestration framework; Azure AI Foundry is the model
provider.

## Quick start

```bash
cp .env.example .env        # fill in Azure values, or leave USE_STUBS=true
docker-compose up --build
```

Then open:
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- Neo4j browser: http://localhost:7474 (neo4j / password)

With `USE_STUBS=true` (default) the whole system runs with no Azure key —
ingestion and agents return canned responses so every panel works. Flip to
`false` and fill in Azure values for real AI calls.

## Architecture

```
Documents -> Ingestion + Extraction -> Neo4j Graph -> FastAPI -> React UI
                  (Azure model)                          |
                                                     Agent layer
                                                  (RCA / Compliance / Historian)
```

| Layer            | Tech                          | Owner    |
|------------------|-------------------------------|----------|
| Ingestion        | PDFPlumber + Azure (LangChain)| Person A |
| Knowledge graph  | Neo4j 5                       | Person A |
| REST API         | FastAPI                       | Person A |
| Agents           | LangChain + Azure             | Person C |
| Frontend         | React + Vite + Cytoscape      | Person B |
| Demo data + Ops  | Docker Compose + pytest       | Person D |

## Repo layout

```
backend/        FastAPI app, graph layer, ingestion, agents
  ai_client.py  single Azure-backed LangChain model (shared)
  agents/       rca, compliance, historian
frontend/       React + Cytoscape knowledge explorer
demo-data/      realistic industrial documents (auto-seeded)
tests/          end-to-end pytest suite
docs/           API contract + entity schema
```

## Running tests

```bash
cd backend && pip install -r requirements.txt
USE_STUBS=true pytest ../tests -v
```

## Local dev without Docker

```bash
# Backend
cd backend && pip install -r requirements.txt
USE_STUBS=true uvicorn main:app --reload

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

## The API contract

See `docs/api_contract.md`. It is locked — changes need a full-team sync.
