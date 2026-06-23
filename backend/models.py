"""
API contract data shapes (Section 5 of the playbook).
These are the locked interfaces B and C build against. Do not change
without a full-team sync.
"""
from typing import Optional
from pydantic import BaseModel, Field


# ---------- Entities ----------
class EntitySummary(BaseModel):
    id: str
    name: str
    type: str  # Equipment | Procedure | FailureMode | Supplier | ComplianceStd
    score: Optional[float] = None


class Backlink(BaseModel):
    type: str            # relationship type
    source_id: str
    source_name: str
    source_type: str


class EntityDetail(BaseModel):
    entity: dict
    backlinks: list[Backlink] = Field(default_factory=list)
    related: list[EntitySummary] = Field(default_factory=list)


# ---------- Graph ----------
class GraphNode(BaseModel):
    id: str
    name: str
    type: str


class GraphRelationship(BaseModel):
    source: str
    target: str
    type: str


class GraphResponse(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    relationships: list[GraphRelationship] = Field(default_factory=list)


# ---------- Ingest ----------
class IngestResponse(BaseModel):
    status: str
    doc_id: str
    entity_count: int


# ---------- Agents ----------
class AgentRequest(BaseModel):
    agent_type: str          # "rca" | "compliance" | "historian"
    entity_id: str
    context: Optional[dict] = None


class Finding(BaseModel):
    text: str
    confidence: float
    citations: list[str] = Field(default_factory=list)


class AgentResult(BaseModel):
    summary: str
    findings: list[Finding] = Field(default_factory=list)
    recommendation: str = ""


class AgentResponse(BaseModel):
    agent_type: str
    entity_id: str
    result: AgentResult
