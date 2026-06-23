"""Agentic intelligence layer (Person C).

Three agents, all built on the shared Azure-backed LangChain model.
Each returns the AgentResult shape from models.py.
"""
from .rca_agent import run_rca
from .compliance_agent import check_compliance
from .historian_agent import equipment_history

__all__ = ["run_rca", "check_compliance", "equipment_history"]
