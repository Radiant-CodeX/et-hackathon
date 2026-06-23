"""
Neo4j graph layer (Person A).

Owns the connection, schema constraints/indexes, writes, and the read
queries that power the API and the agents.

When USE_STUBS=true (the default), every public function returns rich
fixture data so Person B and Person C can develop with zero services
running. Flip USE_STUBS=false once Neo4j is live.
"""
import config

# ---------------------------------------------------------------------------
# Stub fixtures — realistic enough that B can build UI against them and
# C can see the agent context shape. Mirrors the demo-data documents.
# ---------------------------------------------------------------------------
_STUB_NODES = [
    {"id": "Pump-01",        "name": "Pump-01",              "type": "Equipment"},
    {"id": "Compressor-03",  "name": "Compressor-03",        "type": "Equipment"},
    {"id": "HE-01",          "name": "Heat Exchanger HE-01", "type": "Equipment"},
    {"id": "Valve-02",       "name": "Valve-02",             "type": "Equipment"},
    {"id": "Motor-05",       "name": "Motor-05",             "type": "Equipment"},
    {"id": "Bearing wear",   "name": "Bearing wear",         "type": "FailureMode"},
    {"id": "Seal leak",      "name": "Seal leak",            "type": "FailureMode"},
    {"id": "Overheating",    "name": "Overheating",          "type": "FailureMode"},
    {"id": "Fouling",        "name": "Fouling",              "type": "FailureMode"},
    {"id": "SKF",            "name": "SKF",                  "type": "Supplier"},
    {"id": "Flowserve",      "name": "Flowserve",            "type": "Supplier"},
    {"id": "HWP-002",        "name": "Hot Work Permit Procedure HWP-002", "type": "Procedure"},
    {"id": "SOP-011",        "name": "Cooling System Inspection SOP-011", "type": "Procedure"},
    {"id": "OISD-105",       "name": "OISD-105",             "type": "ComplianceStd"},
    {"id": "PESO-2023",      "name": "PESO-2023",            "type": "ComplianceStd"},
]

_STUB_RELS = [
    {"source": "Pump-01",       "target": "Bearing wear",  "type": "HAS_FAILURE_MODE"},
    {"source": "Pump-01",       "target": "Seal leak",     "type": "HAS_FAILURE_MODE"},
    {"source": "Pump-01",       "target": "SKF",           "type": "SUPPLIED_BY"},
    {"source": "Compressor-03", "target": "Bearing wear",  "type": "HAS_FAILURE_MODE"},
    {"source": "Compressor-03", "target": "Overheating",   "type": "HAS_FAILURE_MODE"},
    {"source": "Compressor-03", "target": "SKF",           "type": "SUPPLIED_BY"},
    {"source": "Motor-05",      "target": "Bearing wear",  "type": "HAS_FAILURE_MODE"},
    {"source": "Motor-05",      "target": "SKF",           "type": "SUPPLIED_BY"},
    {"source": "HE-01",         "target": "Fouling",       "type": "HAS_FAILURE_MODE"},
    {"source": "HE-01",         "target": "Flowserve",     "type": "SUPPLIED_BY"},
    {"source": "Valve-02",      "target": "Seal leak",     "type": "HAS_FAILURE_MODE"},
    {"source": "HWP-002",       "target": "Pump-01",       "type": "REFERENCES"},
    {"source": "HWP-002",       "target": "Compressor-03", "type": "REFERENCES"},
    {"source": "HWP-002",       "target": "OISD-105",      "type": "GOVERNED_BY"},
    {"source": "SOP-011",       "target": "HE-01",         "type": "REFERENCES"},
    {"source": "SOP-011",       "target": "PESO-2023",     "type": "GOVERNED_BY"},
]

_STUB_ENTITY_DETAIL = {
    "Pump-01": {
        "entity": {
            "id": "Pump-01", "name": "Pump-01", "type": "Equipment",
            "location": "Bay 3, Cooling Water System",
            "date_commissioned": "2022-03-01",
        },
        "backlinks": [
            {"type": "REFERENCES", "source_id": "HWP-002",
             "source_name": "Hot Work Permit Procedure HWP-002",
             "source_type": "Procedure"},
        ],
        "related": [
            {"id": "Bearing wear", "name": "Bearing wear", "type": "FailureMode"},
            {"id": "Seal leak",    "name": "Seal leak",    "type": "FailureMode"},
            {"id": "SKF",          "name": "SKF",          "type": "Supplier"},
            {"id": "HWP-002",      "name": "Hot Work Permit Procedure HWP-002",
             "type": "Procedure"},
        ],
    },
}


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
_driver = None


def get_driver():
    global _driver
    if _driver is None:
        from neo4j import GraphDatabase
        _driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD),
        )
    return _driver


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def init_schema():
    """Create indexes for sub-second lookups. Idempotent."""
    with get_driver().session() as s:
        s.run("CREATE INDEX entity_id   IF NOT EXISTS FOR (n:Entity) ON (n.id)")
        s.run("CREATE INDEX entity_name IF NOT EXISTS FOR (n:Entity) ON (n.name)")
        s.run("CREATE INDEX entity_type IF NOT EXISTS FOR (n:Entity) ON (n.type)")


# ---------------------------------------------------------------------------
# Writes
# ---------------------------------------------------------------------------

def write_entities(data: dict):
    """
    data = {"entities": [...], "relationships": [...]}
    Every node carries :Entity plus its specific type label.
    Safe to call repeatedly — MERGE is idempotent.
    """
    if config.USE_STUBS:
        return
    with get_driver().session() as s:
        for e in data.get("entities", []):
            s.run(
                "MERGE (n:Entity {id: $id}) "
                "SET n.name = $name, n.type = $type, n += $meta",
                id=e["name"],
                name=e["name"],
                type=e.get("type", "Unknown"),
                meta=e.get("metadata", {}),
            )
        for r in data.get("relationships", []):
            s.run(
                "MATCH (a:Entity {id: $s}), (b:Entity {id: $t}) "
                "MERGE (a)-[rel:RELATED {type: $ty}]->(b)",
                s=r["source"], t=r["target"], ty=r.get("type", "RELATED"),
            )


# ---------------------------------------------------------------------------
# Reads — public API
# ---------------------------------------------------------------------------

def list_entities(limit: int = 100) -> list[dict]:
    if config.USE_STUBS:
        return _STUB_NODES[:limit]
    with get_driver().session() as s:
        rows = s.run(
            "MATCH (n:Entity) "
            "RETURN n.id AS id, n.name AS name, n.type AS type "
            "ORDER BY n.name LIMIT $limit",
            limit=limit,
        )
        return [dict(r) for r in rows]


def get_entity(entity_id: str) -> dict | None:
    if config.USE_STUBS:
        return _STUB_ENTITY_DETAIL.get(
            entity_id,
            {
                "entity":    {"id": entity_id, "name": entity_id, "type": "Equipment"},
                "backlinks": [],
                "related":   [],
            },
        )
    with get_driver().session() as s:
        rec = s.run(
            "MATCH (n:Entity {id: $id}) "
            "OPTIONAL MATCH (n)<-[r]-(m:Entity) "
            "RETURN n AS entity, "
            "collect(DISTINCT {type: r.type, source_id: m.id, "
            "  source_name: m.name, source_type: m.type}) AS backlinks",
            id=entity_id,
        ).single()
        if not rec:
            return None
        entity = dict(rec["entity"])
        backlinks = [b for b in rec["backlinks"] if b["source_id"]]
        related = _related(s, entity_id)
        return {"entity": entity, "backlinks": backlinks, "related": related}


def _related(session, entity_id: str) -> list[dict]:
    rows = session.run(
        "MATCH (n:Entity {id: $id})-[r]-(m:Entity) "
        "RETURN DISTINCT m.id AS id, m.name AS name, m.type AS type LIMIT 25",
        id=entity_id,
    )
    return [dict(r) for r in rows]


def search(q: str) -> list[dict]:
    if config.USE_STUBS:
        q_lower = q.lower()
        return [
            n for n in _STUB_NODES
            if q_lower in n["name"].lower() or q_lower in n["type"].lower()
        ]
    with get_driver().session() as s:
        rows = s.run(
            "MATCH (n:Entity) "
            "WHERE toLower(n.name) CONTAINS toLower($q) "
            "   OR toLower(coalesce(n.type,'')) CONTAINS toLower($q) "
            "RETURN n.id AS id, n.name AS name, n.type AS type LIMIT 50",
            q=q,
        )
        return [dict(r) for r in rows]


def full_graph() -> dict:
    if config.USE_STUBS:
        return {"nodes": _STUB_NODES, "relationships": _STUB_RELS}
    with get_driver().session() as s:
        nodes = [
            dict(r)
            for r in s.run(
                "MATCH (n:Entity) "
                "RETURN n.id AS id, n.name AS name, n.type AS type"
            )
        ]
        rels = [
            dict(r)
            for r in s.run(
                "MATCH (a:Entity)-[r]->(b:Entity) "
                "RETURN a.id AS source, b.id AS target, r.type AS type"
            )
        ]
        return {"nodes": nodes, "relationships": rels}


# ---------------------------------------------------------------------------
# Agent helper queries (Person C calls these via equipment_context)
# ---------------------------------------------------------------------------

def equipment_context(entity_id: str) -> dict:
    """Bundle everything an agent needs about one entity in a single call."""
    detail = get_entity(entity_id)
    if not detail:
        return {"entity": {"id": entity_id}, "backlinks": [], "related": []}
    return detail


def get_equipment_history(entity_id: str) -> list[dict]:
    """Return all FailureMode nodes connected to this equipment, with metadata."""
    if config.USE_STUBS:
        return [
            n for n in _STUB_NODES
            if n["type"] == "FailureMode"
            and any(
                r["source"] == entity_id and r["target"] == n["id"]
                for r in _STUB_RELS
            )
        ]
    with get_driver().session() as s:
        rows = s.run(
            "MATCH (e:Entity {id: $id})-[:RELATED {type: 'HAS_FAILURE_MODE'}]->(f:Entity) "
            "RETURN f.id AS id, f.name AS name, f.type AS type",
            id=entity_id,
        )
        return [dict(r) for r in rows]


def get_similar_failures(entity_id: str) -> list[dict]:
    """Return other Equipment that share a FailureMode with this entity."""
    if config.USE_STUBS:
        my_failure_targets = {
            r["target"] for r in _STUB_RELS
            if r["source"] == entity_id and r["type"] == "HAS_FAILURE_MODE"
        }
        similar_equipment = {
            r["source"] for r in _STUB_RELS
            if r["type"] == "HAS_FAILURE_MODE"
            and r["target"] in my_failure_targets
            and r["source"] != entity_id
        }
        return [n for n in _STUB_NODES if n["id"] in similar_equipment]
    with get_driver().session() as s:
        rows = s.run(
            "MATCH (e:Entity {id: $id})-[:RELATED {type: 'HAS_FAILURE_MODE'}]->(f:Entity)"
            "<-[:RELATED {type: 'HAS_FAILURE_MODE'}]-(other:Entity) "
            "WHERE other.id <> $id "
            "RETURN DISTINCT other.id AS id, other.name AS name, other.type AS type",
            id=entity_id,
        )
        return [dict(r) for r in rows]


def get_supplier_timeline(entity_id: str) -> list[dict]:
    """Return Supplier nodes linked to this equipment."""
    if config.USE_STUBS:
        supplier_ids = {
            r["target"] for r in _STUB_RELS
            if r["source"] == entity_id and r["type"] == "SUPPLIED_BY"
        }
        return [n for n in _STUB_NODES if n["id"] in supplier_ids]
    with get_driver().session() as s:
        rows = s.run(
            "MATCH (e:Entity {id: $id})-[:RELATED {type: 'SUPPLIED_BY'}]->(s:Entity) "
            "RETURN s.id AS id, s.name AS name, s.type AS type",
            id=entity_id,
        )
        return [dict(r) for r in rows]
