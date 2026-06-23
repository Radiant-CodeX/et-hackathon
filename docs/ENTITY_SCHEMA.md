# Entity Schema

> Locked at Hour 2. Do not change without a full-team sync.

## Node Types

Every node has `id`, `name`, `type`, and an optional `metadata` bag.

| Node type | Key fields | Example |
|-----------|-----------|---------|
| `Equipment` | `date_commissioned`, `location` | Pump-01, Compressor-03 |
| `Procedure` | `revision`, `references[]` | HWP-002, SOP-011 |
| `FailureMode` | `severity`, `description` | Bearing wear, Seal leak |
| `Supplier` | `parts_supplied[]` | SKF, Flowserve |
| `ComplianceStd` | `authority`, `clause` | OISD-105, PESO-2023 |

## Relationship Types

```
(Equipment)     -[:HAS_FAILURE_MODE]-> (FailureMode)
(Procedure)     -[:REFERENCES]->       (Equipment)
(MaintenanceLog)-[:CAUSED_BY]->        (FailureMode)
(Equipment)     -[:SUPPLIED_BY]->      (Supplier)
(Procedure)     -[:GOVERNED_BY]->      (ComplianceStd)
```

## Neo4j Storage

All nodes carry the base label `:Entity` plus their specific type label.  
All relationships are stored as `[:RELATED {type: "<REL_TYPE>"}]` for schema flexibility.

Indexes created on startup (see `graph.init_schema`):
- `entity_id`   on `(n:Entity).id`
- `entity_name` on `(n:Entity).name`
- `entity_type` on `(n:Entity).type`

## JSON representation (REST API)

```json
{
  "id":   "Pump-01",
  "name": "Pump-01",
  "type": "Equipment",
  "date_commissioned": "2022-03-01",
  "location": "Bay 3, Cooling Water System",
  "metadata": {}
}
```
