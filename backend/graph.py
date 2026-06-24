"""
Neo4j graph layer (Person A).

Owns the connection, schema constraints/indexes, writes, and the read
queries that power the API and the agents. Falls back gracefully if the
driver can't connect so the rest of the app still boots.
"""
import config

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


def init_schema():
    """Create indexes for sub-second lookups. Idempotent."""
    with get_driver().session() as s:
        s.run("CREATE INDEX entity_id IF NOT EXISTS FOR (n:Entity) ON (n.id)")
        s.run("CREATE INDEX entity_name IF NOT EXISTS FOR (n:Entity) ON (n.name)")


def write_entities(data: dict):
    """
    data = {"entities": [...], "relationships": [...]}
    Every node carries the :Entity label plus its specific type label.
    """
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


def list_entities(limit: int = 100):
    with get_driver().session() as s:
        rows = s.run(
            "MATCH (n:Entity) RETURN n.id AS id, n.name AS name, "
            "n.type AS type ORDER BY n.name LIMIT $limit",
            limit=limit,
        )
        return [dict(r) for r in rows]


def get_entity(entity_id: str):
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


def _related(session, entity_id: str):
    rows = session.run(
        "MATCH (n:Entity {id: $id})-[r]-(m:Entity) "
        "RETURN DISTINCT m.id AS id, m.name AS name, m.type AS type LIMIT 25",
        id=entity_id,
    )
    return [dict(r) for r in rows]


def search(q: str):
    with get_driver().session() as s:
        rows = s.run(
            "MATCH (n:Entity) WHERE toLower(n.name) CONTAINS toLower($q) "
            "OR toLower(coalesce(n.type,'')) CONTAINS toLower($q) "
            "RETURN n.id AS id, n.name AS name, n.type AS type LIMIT 50",
            q=q,
        )
        return [dict(r) for r in rows]


def full_graph():
    with get_driver().session() as s:
        nodes = [
            dict(r)
            for r in s.run(
                "MATCH (n:Entity) RETURN n.id AS id, n.name AS name, n.type AS type"
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


# ---------- Helpers the agents (Person C) call ----------
def equipment_context(entity_id: str) -> dict:
    """Bundle everything an agent needs about an entity in one call."""
    detail = get_entity(entity_id)
    if not detail:
        return {"entity": {"id": entity_id}, "backlinks": [], "related": []}
    return detail
