import { describe, test, expect } from "vitest";
import { mockGraph, mockSearch, mockEntityDetail, mockAgentRun } from "./mockClient";

describe("mock API (A3)", () => {
  test("mock graph has nodes and relationships", () => {
    expect(mockGraph.nodes.length).toBeGreaterThan(0);
    expect(mockGraph.relationships.length).toBeGreaterThan(0);
  });

  test("search returns scored matches", () => {
    const res = mockSearch("Pump");
    expect(res.length).toBeGreaterThan(0);
    expect(res[0]).toHaveProperty("score");
  });

  test("entity detail includes backlinks and related", () => {
    const d = mockEntityDetail("Pump-01");
    expect(d.entity.id).toBe("Pump-01");
    expect(Array.isArray(d.backlinks)).toBe(true);
    expect(Array.isArray(d.related)).toBe(true);
  });

  test("agent run returns structured result", () => {
    const r = mockAgentRun("rca", "Pump-01");
    expect(r.result).toHaveProperty("summary");
    expect(r.result.findings[0]).toHaveProperty("confidence");
  });
});
