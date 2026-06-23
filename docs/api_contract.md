# API Contract (LOCKED)

Locked at Hour 2. Changes require a full-team sync. B and C build against
these shapes; A implements them.

## Entity schema

Node types (all carry the `:Entity` label plus a `type` property):

| Type          | Key fields                                  |
|---------------|---------------------------------------------|
| Equipment     | id, name, type, metadata{location, ...}     |
| Procedure     | id, name, type, metadata{revision, ...}     |
| FailureMode   | id, name, type, metadata{severity, ...}     |
| Supplier      | id, name, type, metadata{}                  |
| ComplianceStd | id, name, type, metadata{authority, clause} |

Relationship types:

```
(Equipment)-[:RELATED {type:"HAS_FAILURE_MODE"}]->(FailureMode)
(Procedure)-[:RELATED {type:"REFERENCES"}]->(Equipment)
(Equipment)-[:RELATED {type:"CAUSED_BY"}]->(FailureMode)
(Equipment)-[:RELATED {type:"SUPPLIED_BY"}]->(Supplier)
(Procedure)-[:RELATED {type:"GOVERNED_BY"}]->(ComplianceStd)
```

## REST endpoints

| Method + Route            | Purpose                  | Returns                              |
|---------------------------|--------------------------|--------------------------------------|
| GET  /health              | Liveness + config        | { status, azure_configured, use_stubs } |
| POST /ingest              | Upload + extract a doc   | { status, doc_id, entity_count }     |
| GET  /entities            | Paginated entity list    | [ { id, name, type } ]               |
| GET  /entities/{id}       | Entity detail + backlinks| { entity, backlinks[], related[] }   |
| GET  /graph/relationships | Full graph for viz       | { nodes[], relationships[] }         |
| GET  /search?q=           | Full-text entity search  | [ { id, name, type } ]               |
| POST /agents/run          | Trigger an agent         | { agent_type, entity_id, result }    |

## Agent contract

```
POST /agents/run
Request:  { "agent_type": "rca" | "compliance" | "historian",
            "entity_id": "Pump-01",
            "context": { optional } }

Response: { "agent_type": "rca",
            "entity_id": "Pump-01",
            "result": {
              "summary": str,
              "findings": [ { "text": str, "confidence": float,
                             "citations": [str] } ],
              "recommendation": str } }
```

## Stub mode

`USE_STUBS=true` makes ingestion and agents return canned responses, so the
full app runs with no Azure key. Person A flips it off once `ai_client` is
wired and Azure is configured.
