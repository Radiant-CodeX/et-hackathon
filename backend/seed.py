"""
Seed script (Person D drives the data; Person A wires the loader).

Ingests every document in demo-data/ so the system is populated the
moment `docker-compose up` finishes. Run automatically by the backend
entrypoint or manually: `python seed.py`.
"""
import os
import time

import graph
import ingest

DEMO_DIR = os.environ.get("DEMO_DIR", "/app/demo-data")


def wait_for_neo4j(retries: int = 30):
    for i in range(retries):
        try:
            graph.init_schema()
            return True
        except Exception:
            print(f"[seed] waiting for Neo4j ({i + 1}/{retries})...")
            time.sleep(2)
    return False


def seed():
    if not wait_for_neo4j():
        print("[seed] Neo4j unavailable; skipping seed.")
        return
    if not os.path.isdir(DEMO_DIR):
        print(f"[seed] no demo dir at {DEMO_DIR}; skipping.")
        return
    count = 0
    for fname in sorted(os.listdir(DEMO_DIR)):
        path = os.path.join(DEMO_DIR, fname)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as f:
            result = ingest.ingest_document(fname, f.read())
        print(f"[seed] {fname}: {result['entity_count']} entities")
        count += 1
    print(f"[seed] done. {count} documents ingested.")


if __name__ == "__main__":
    seed()
