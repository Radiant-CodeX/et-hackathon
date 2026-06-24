/* ============================================================
   Mock API client (Section A3)
   Lets Person B build the entire UI before Person A / C ship
   real endpoints. Demo data deliberately encodes the RCA
   "discovery" pattern: three machines all fail on SKF bearings.
   ============================================================ */

export const mockGraph = {
  nodes: [
    { id: "Pump-01", name: "Pump-01", type: "Equipment" },
    { id: "Pump-02", name: "Pump-02", type: "Equipment" },
    { id: "Compressor-07", name: "Compressor-07", type: "Equipment" },
    { id: "Bearing-Failure", name: "Bearing Failure", type: "FailureMode" },
    { id: "Cavitation", name: "Cavitation", type: "FailureMode" },
    { id: "SKF", name: "SKF", type: "Supplier" },
    { id: "SOP-Maint-12", name: "SOP-Maint-12", type: "Procedure" },
    { id: "Hot-Work-Permit", name: "Hot Work Permit", type: "Procedure" },
    { id: "OISD-118", name: "OISD-118", type: "ComplianceStd" },
  ],
  relationships: [
    { source: "Pump-01", target: "Bearing-Failure", type: "HAS_FAILURE_MODE" },
    { source: "Pump-02", target: "Bearing-Failure", type: "HAS_FAILURE_MODE" },
    { source: "Compressor-07", target: "Bearing-Failure", type: "HAS_FAILURE_MODE" },
    { source: "Pump-01", target: "Cavitation", type: "HAS_FAILURE_MODE" },
    { source: "Pump-01", target: "SKF", type: "SUPPLIED_BY" },
    { source: "Pump-02", target: "SKF", type: "SUPPLIED_BY" },
    { source: "Compressor-07", target: "SKF", type: "SUPPLIED_BY" },
    { source: "SOP-Maint-12", target: "Pump-01", type: "REFERENCES" },
    { source: "SOP-Maint-12", target: "OISD-118", type: "GOVERNED_BY" },
    { source: "Hot-Work-Permit", target: "OISD-118", type: "GOVERNED_BY" },
  ],
};

const META = {
  "Pump-01": {
    type: "Equipment",
    date_commissioned: "2019-04-12",
    location: "Unit-3 / Bay-A",
    criticality: "High",
  },
  "Pump-02": { type: "Equipment", date_commissioned: "2020-01-08", location: "Unit-3 / Bay-B", criticality: "Medium" },
  "Compressor-07": { type: "Equipment", date_commissioned: "2018-11-20", location: "Unit-5 / Compressor House", criticality: "High" },
  "Bearing-Failure": { type: "FailureMode", severity: "Critical", description: "Premature bearing wear leading to abnormal vibration" },
  "Cavitation": { type: "FailureMode", severity: "Medium", description: "Impeller surface pitting from vapour collapse" },
  SKF: { type: "Supplier", parts_supplied: ["Bearing #6309", "Bearing #6204"], qualification: "Tier-2" },
  "SOP-Maint-12": { type: "Procedure", revision: "Rev-4", references: ["Pump-01", "OISD-118"] },
  "Hot-Work-Permit": { type: "Procedure", revision: "Rev-2", references: ["OISD-118"] },
  "OISD-118": { type: "ComplianceStd", authority: "OISD", clause: "Clause 7.3 — Permit to Work" },
};

function buildEntity(id) {
  const base = mockGraph.nodes.find((n) => n.id === id) || { id, name: id, type: "Equipment" };
  const backlinks = mockGraph.relationships
    .filter((r) => r.target === id)
    .map((r) => ({ id: r.source, name: r.source, type: nodeType(r.source), rel: r.type }));
  const related = mockGraph.relationships
    .filter((r) => r.source === id)
    .map((r) => ({ id: r.target, name: r.target, type: nodeType(r.target), rel: r.type }));
  return {
    entity: { ...base, metadata: META[id] || {} },
    backlinks,
    related,
  };
}

function nodeType(id) {
  return (mockGraph.nodes.find((n) => n.id === id) || {}).type || "Equipment";
}

export const mockEntities = mockGraph.nodes.map(({ id, name, type }) => ({ id, name, type }));

export function mockSearch(q) {
  const query = (q || "").toLowerCase();
  return mockEntities
    .filter((e) => e.name.toLowerCase().includes(query) || e.type.toLowerCase().includes(query))
    .map((e, i) => ({ ...e, score: +(0.97 - i * 0.05).toFixed(2) }));
}

export function mockEntityDetail(id) {
  return buildEntity(id);
}

const AGENT_RESULTS = {
  rca: {
    summary:
      "Recurring bearing-failure pattern detected across Pump-01, Pump-02 and Compressor-07 — all sourced from supplier SKF. This systemic link spans three separate incidents that individual maintenance reviews treated as unrelated.",
    findings: [
      { text: "Pump-01 logged 2 bearing failures (Dec-2024, Mar-2025), both SKF #6309.", confidence: 0.91, citations: ["maint-log-pump01:chunk-2"] },
      { text: "Compressor-07 failed on the same SKF bearing line within 90 days.", confidence: 0.86, citations: ["maint-log-comp07:chunk-1"] },
      { text: "No design or operating-condition difference explains the common failure — supplier is the shared variable.", confidence: 0.78, citations: ["rca-corr:chunk-4"] },
    ],
    recommendation: "Review SKF bearing-line qualification and audit incoming-inspection records for batch defects.",
  },
  compliance: {
    summary:
      "A required permit sign-off is missing on the latest hot-work activity referenced by SOP-Maint-12, creating a gap against OISD-118 Clause 7.3 (Permit to Work) that would surface in an audit.",
    findings: [
      { text: "Hot Work Permit Rev-2 lacks the area-authority counter-signature mandated by OISD-118 §7.3.", confidence: 0.88, citations: ["permit-hw:chunk-1", "oisd-118:clause-7.3"] },
      { text: "SOP-Maint-12 references the permit but does not enforce sign-off verification.", confidence: 0.74, citations: ["sop-maint12:chunk-3"] },
    ],
    recommendation: "Add a mandatory counter-sign verification step to SOP-Maint-12 before audit cycle.",
  },
  historian: {
    summary:
      "Lifetime narrative for the selected asset assembled from maintenance, failure and supplier records — surfacing the full timeline in seconds.",
    findings: [
      { text: "Commissioned 2019-04-12 in Unit-3 / Bay-A; classified High criticality.", confidence: 0.95, citations: ["asset-reg:pump01"] },
      { text: "3 maintenance events, 2 corrective (bearing), 1 preventive (seal/impeller).", confidence: 0.9, citations: ["maint-log-pump01:chunk-1"] },
      { text: "All bearing parts sourced from SKF; cumulative repair cost ₹13,400.", confidence: 0.83, citations: ["maint-log-pump01:chunk-2"] },
    ],
    recommendation: "Flag for reliability review given repeat corrective interventions within 18 months.",
  },
};

export function mockAgentRun(agent_type, entity_id) {
  const result = AGENT_RESULTS[agent_type] || AGENT_RESULTS.rca;
  return { agent_type, entity_id, result };
}
