"""
FastAPI app (Person A owns; Person C owns the /agents route body).

Implements every route in the Section 5 API contract. Graph and agent
calls degrade gracefully so the app boots even before Neo4j or Azure
are wired.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import config
import graph
import ingest
import agents
from models import (
    IngestResponse, EntitySummary, EntityDetail, GraphResponse,
    AgentRequest, AgentResponse, AgentResult,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        graph.init_schema()
    except Exception as e:
        print(f"[startup] Neo4j not ready ({e}); continuing.")
    yield


app = FastAPI(
    title="Industrial Knowledge Intelligence",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "azure_configured": config.azure_configured(),
        "use_stubs": config.USE_STUBS,
    }


@app.post("/ingest", response_model=IngestResponse)
async def ingest_route(file: UploadFile = File(...)):
    raw = await file.read()
    try:
        return ingest.ingest_document(file.filename, raw)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {e}")


@app.get("/entities", response_model=list[EntitySummary])
def entities_route(limit: int = 100):
    try:
        return graph.list_entities(limit)
    except Exception:
        return []


@app.get("/entities/{entity_id}", response_model=EntityDetail)
def entity_detail_route(entity_id: str):
    detail = graph.get_entity(entity_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Entity not found")
    return detail


@app.get("/graph/relationships", response_model=GraphResponse)
def graph_route():
    try:
        return graph.full_graph()
    except Exception:
        return {"nodes": [], "relationships": []}


@app.get("/search", response_model=list[EntitySummary])
def search_route(q: str):
    try:
        return graph.search(q)
    except Exception:
        return []


@app.post("/agents/run", response_model=AgentResponse)
def agents_route(req: AgentRequest):
    detail = graph.equipment_context(req.entity_id)
    dispatch = {
        "rca": agents.run_rca,
        "compliance": agents.check_compliance,
        "historian": agents.equipment_history,
    }
    fn = dispatch.get(req.agent_type)
    if not fn:
        raise HTTPException(status_code=400, detail="Unknown agent_type")
    result = fn(req.entity_id, detail)
    return {
        "agent_type": req.agent_type,
        "entity_id": req.entity_id,
        "result": AgentResult(**result),
    }
