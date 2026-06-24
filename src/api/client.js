/* ============================================================
   API client (Section D) — talks to Person A's FastAPI backend
   at http://localhost:8000, per the locked API contract (§5.2).

   Design: every call tries the real backend first, and on any
   failure transparently falls back to the mock client. This is
   what keeps Person B unblocked (Section A) while making the
   exact same UI light up against the real backend (Section B)
   with zero code changes. `apiMode` reports which path served
   the last request so the UI can show a LIVE / DEMO badge.
   ============================================================ */

import axios from "axios";
import {
  mockGraph,
  mockEntities,
  mockSearch,
  mockEntityDetail,
  mockAgentRun,
} from "./mockClient";

const BASE_URL = import.meta?.env?.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 8000,
  headers: { "Content-Type": "application/json" },
});

// Reactive-ish mode flag the Dashboard can read after each call.
export const apiState = { mode: "unknown" }; // "live" | "mock" | "unknown"

async function withFallback(realCall, mockValue) {
  try {
    const data = await realCall();
    apiState.mode = "live";
    return data;
  } catch (err) {
    apiState.mode = "mock";
    return mockValue;
  }
}

export const ikip = {
  getMode: () => apiState.mode,

  // GET /graph/relationships
  getGraph: () =>
    withFallback(async () => (await api.get("/graph/relationships")).data, mockGraph),

  // GET /entities
  getEntities: () =>
    withFallback(async () => (await api.get("/entities")).data, mockEntities),

  // GET /entities/{id}
  getEntity: (id) =>
    withFallback(
      async () => (await api.get(`/entities/${encodeURIComponent(id)}`)).data,
      mockEntityDetail(id)
    ),

  // GET /search?q=
  search: (q) =>
    withFallback(
      async () => (await api.get("/search", { params: { q } })).data,
      mockSearch(q)
    ),

  // POST /agents/run
  runAgent: (agent_type, entity_id, context = {}) =>
    withFallback(
      async () =>
        (await api.post("/agents/run", { agent_type, entity_id, context })).data,
      mockAgentRun(agent_type, entity_id)
    ),
};

export default ikip;
