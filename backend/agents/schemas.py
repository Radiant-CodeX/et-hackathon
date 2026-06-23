"""Schema definitions for agent I/O (shared across all agents)."""
from typing import Optional, List
from pydantic import BaseModel, Field


class Finding(BaseModel):
    """A single finding from an agent with evidence."""
    text: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    citations: List[str] = Field(default_factory=list)


class AgentResult(BaseModel):
    """The standard output format for all agents."""
    summary: str
    findings: List[Finding] = Field(default_factory=list)
    recommendation: str


class EquipmentContext(BaseModel):
    """Context about equipment retrieved from the graph."""
    entity_id: str
    entity_name: str
    entity_type: str
    metadata: dict = Field(default_factory=dict)
    related_failures: List[dict] = Field(default_factory=list)
    related_procedures: List[dict] = Field(default_factory=list)
    related_suppliers: List[dict] = Field(default_factory=list)
    maintenance_records: List[dict] = Field(default_factory=list)
