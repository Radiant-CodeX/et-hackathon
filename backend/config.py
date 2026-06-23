"""Central configuration. All env vars are read here, once."""
import os

# --- Neo4j ---
NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://neo4j:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")

# --- Azure AI Foundry (model provider; LangChain is the framework) ---
AZURE_INFERENCE_ENDPOINT = os.environ.get("AZURE_INFERENCE_ENDPOINT", "")
AZURE_INFERENCE_KEY = os.environ.get("AZURE_INFERENCE_KEY", "")
AZURE_DEPLOYMENT_NAME = os.environ.get("AZURE_DEPLOYMENT_NAME", "gpt-4o")
AZURE_API_VERSION = os.environ.get("AZURE_API_VERSION", "2024-10-21")
AZURE_EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")

# --- App behaviour ---
# When true, AI calls return canned responses so the app runs with no Azure key.
# Person A flips this off once ai_client is wired; great for B/C/D local dev.
USE_STUBS = os.environ.get("USE_STUBS", "true").lower() == "true"

FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")


def azure_configured() -> bool:
    return bool(AZURE_INFERENCE_ENDPOINT and AZURE_INFERENCE_KEY)
