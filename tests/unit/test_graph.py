"""Unit tests for graph.py stub mode — no Neo4j needed."""
import os
import sys

os.environ["USE_STUBS"] = "true"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

import graph


# ---------- full_graph ----------

def test_full_graph_returns_nodes_and_rels():
    result = graph.full_graph()
    assert "nodes" in result
    assert "relationships" in result
    assert len(result["nodes"]) > 0
    assert len(result["relationships"]) > 0


def test_full_graph_nodes_have_required_fields():
    nodes = graph.full_graph()["nodes"]
    for n in nodes:
        assert "id" in n
        assert "name" in n
        assert "type" in n


def test_full_graph_rels_have_required_fields():
    rels = graph.full_graph()["relationships"]
    for r in rels:
        assert "source" in r
        assert "target" in r
        assert "type" in r


def test_full_graph_known_node_types():
    types = {n["type"] for n in graph.full_graph()["nodes"]}
    assert "Equipment" in types
    assert "FailureMode" in types
    assert "Supplier" in types


# ---------- list_entities ----------

def test_list_entities_returns_list():
    result = graph.list_entities()
    assert isinstance(result, list)
    assert len(result) > 0


def test_list_entities_respects_limit():
    result = graph.list_entities(limit=3)
    assert len(result) <= 3


def test_list_entities_fields():
    for e in graph.list_entities():
        assert "id" in e
        assert "name" in e
        assert "type" in e


# ---------- get_entity ----------

def test_get_entity_pump01_returns_detail():
    result = graph.get_entity("Pump-01")
    assert result is not None
    assert result["entity"]["id"] == "Pump-01"
    assert "backlinks" in result
    assert "related" in result


def test_get_entity_unknown_returns_generic_stub():
    result = graph.get_entity("Unknown-99")
    assert result is not None
    assert result["entity"]["id"] == "Unknown-99"
    assert result["backlinks"] == []


def test_get_entity_pump01_has_related():
    result = graph.get_entity("Pump-01")
    related_types = {r["type"] for r in result["related"]}
    assert "FailureMode" in related_types or "Supplier" in related_types


# ---------- search ----------

def test_search_pump_returns_results():
    results = graph.search("Pump")
    assert len(results) > 0
    assert any("Pump" in r["name"] for r in results)


def test_search_skf_returns_supplier():
    results = graph.search("SKF")
    assert len(results) > 0
    assert results[0]["type"] == "Supplier"


def test_search_no_match_returns_empty():
    results = graph.search("ZZZNOTAREAL")
    assert results == []


def test_search_case_insensitive():
    upper = graph.search("PUMP")
    lower = graph.search("pump")
    assert len(upper) == len(lower)


# ---------- agent helpers ----------

def test_get_equipment_history_pump01():
    failures = graph.get_equipment_history("Pump-01")
    assert isinstance(failures, list)
    assert any(f["type"] == "FailureMode" for f in failures)


def test_get_similar_failures_pump01():
    similar = graph.get_similar_failures("Pump-01")
    assert isinstance(similar, list)
    ids = [s["id"] for s in similar]
    # Compressor-03 and Motor-05 share Bearing wear with Pump-01
    assert "Compressor-03" in ids or "Motor-05" in ids


def test_get_supplier_timeline_pump01():
    suppliers = graph.get_supplier_timeline("Pump-01")
    assert isinstance(suppliers, list)
    assert any(s["id"] == "SKF" for s in suppliers)


def test_get_equipment_history_unknown_entity():
    result = graph.get_equipment_history("Unknown-99")
    assert result == []


def test_equipment_context_returns_bundle():
    ctx = graph.equipment_context("Pump-01")
    assert "entity" in ctx
    assert "backlinks" in ctx
    assert "related" in ctx
