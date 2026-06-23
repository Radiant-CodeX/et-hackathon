import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: BASE });

export const getGraph = () => api.get("/graph/relationships").then((r) => r.data);
export const getEntities = (limit = 100) =>
  api.get("/entities", { params: { limit } }).then((r) => r.data);
export const getEntity = (id) =>
  api.get(`/entities/${encodeURIComponent(id)}`).then((r) => r.data);
export const search = (q) =>
  api.get("/search", { params: { q } }).then((r) => r.data);
export const runAgent = (agent_type, entity_id) =>
  api.post("/agents/run", { agent_type, entity_id }).then((r) => r.data);
export const ingest = (file) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/ingest", form).then((r) => r.data);
};
