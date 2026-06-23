import { useEffect, useState } from "react";
import { getEntity, runAgent } from "../api/client";

const AGENTS = [
  { type: "rca", label: "Run root cause analysis" },
  { type: "compliance", label: "Check compliance" },
  { type: "historian", label: "Equipment history" },
];

export default function EntityPanel({ entity }) {
  const [detail, setDetail] = useState(null);
  const [agentResult, setAgentResult] = useState(null);
  const [running, setRunning] = useState(null);

  useEffect(() => {
    setDetail(null);
    setAgentResult(null);
    if (!entity) return;
    getEntity(entity.id)
      .then(setDetail)
      .catch(() => setDetail(null));
  }, [entity]);

  if (!entity) return null;

  const trigger = (type) => {
    setRunning(type);
    setAgentResult(null);
    runAgent(type, entity.id)
      .then((res) => setAgentResult(res))
      .catch(() => setAgentResult(null))
      .finally(() => setRunning(null));
  };

  return (
    <div>
      <h2>{entity.label}</h2>
      <div className="type-label">{entity.type}</div>

      <div className="detail-section">
        <h3>Intelligence agents</h3>
        <div className="agent-buttons">
          {AGENTS.map((a) => (
            <button
              key={a.type}
              className="agent-btn"
              onClick={() => trigger(a.type)}
              disabled={running !== null}
            >
              {running === a.type ? "Running..." : a.label}
            </button>
          ))}
        </div>
        {agentResult && <AgentResult result={agentResult.result} />}
      </div>

      {detail?.backlinks?.length > 0 && (
        <div className="detail-section">
          <h3>Referenced by</h3>
          {detail.backlinks.map((b, i) => (
            <div key={i} className="list-item">
              <span className={`dot type-${b.source_type}`} />
              {b.source_name}
              <span className="badge">{b.type}</span>
            </div>
          ))}
        </div>
      )}

      {detail?.related?.length > 0 && (
        <div className="detail-section">
          <h3>Related entities</h3>
          {detail.related.map((r) => (
            <div key={r.id} className="list-item">
              <span className={`dot type-${r.type}`} />
              {r.name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function AgentResult({ result }) {
  if (!result) return null;
  return (
    <div className="agent-result">
      <div className="summary">{result.summary}</div>
      {(result.findings || []).map((f, i) => (
        <div key={i} className="finding">
          {f.text}
          <span className="confidence">
            {Math.round((f.confidence || 0) * 100)}%
          </span>
          {(f.citations || []).length > 0 && (
            <div className="citation">{f.citations.join(", ")}</div>
          )}
        </div>
      ))}
      {result.recommendation && (
        <div className="recommendation">{result.recommendation}</div>
      )}
    </div>
  );
}
