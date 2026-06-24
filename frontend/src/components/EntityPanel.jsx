import { MousePointerClick } from "lucide-react";
import { colorFor, TYPE_LABELS } from "./nodeTypes";
import AgentButtons from "./AgentButtons";
import AgentResult from "./AgentResult";
import Loading from "./Loading";

/**
 * Right panel (TDD A6 / B3 / B5). Shows entity properties, backlinks,
 * related nodes, the three agent buttons and the structured agent result.
 *
 * Props:
 *   entity:        { id, name, type, metadata }
 *   detail:        { backlinks[], related[] }
 *   loading:       detail fetch in flight
 *   onSelectLink:  (id) => void
 *   onRunAgent:    (agentType) => void
 *   runningAgent:  agent_type in flight | null
 *   agentResult:   { agent_type, result }
 */
export default function EntityPanel({
  entity,
  detail,
  loading,
  onSelectLink,
  onRunAgent,
  runningAgent,
  agentResult,
}) {
  if (!entity) {
    return (
      <div className="entity-detail empty" data-testid="entity-empty">
        <div className="empty-inner">
          <MousePointerClick size={34} />
          <div>Select an entity from the graph or list to inspect its details.</div>
        </div>
      </div>
    );
  }

  const meta = entity.metadata || {};
  const metaEntries = Object.entries(meta).filter(
    ([, v]) => v !== null && v !== undefined && v !== ""
  );
  const backlinks = detail?.backlinks || [];
  const related = detail?.related || [];

  return (
    <div className="entity-detail" data-testid="entity-detail">
      <div className="detail-title">
        <span className="badge" style={{ background: colorFor(entity.type) }}>
          {entity.name?.[0] || "?"}
        </span>
        <div>
          <h2>{entity.name}</h2>
          <span className="detail-type" style={{ color: colorFor(entity.type) }}>
            {TYPE_LABELS[entity.type] || entity.type}
          </span>
        </div>
      </div>

      {metaEntries.length > 0 && (
        <div className="meta-grid">
          {metaEntries.map(([k, v]) => (
            <div className="meta-row" key={k}>
              <span className="k">{k.replace(/_/g, " ")}</span>
              <span className="v">{Array.isArray(v) ? v.join(", ") : String(v)}</span>
            </div>
          ))}
        </div>
      )}

      {loading && <Loading label="Loading relationships…" />}

      {backlinks.length > 0 && (
        <>
          <div className="detail-section-title">Backlinks · {backlinks.length}</div>
          {backlinks.map((b) => (
            <div className="link-chip" key={`bl-${b.id}-${b.rel}`} onClick={() => onSelectLink?.(b.id)}>
              <span className="type-dot" style={{ background: colorFor(b.type) }} />
              {b.name}
              <span className="rel">{(b.rel || "").toLowerCase()}</span>
            </div>
          ))}
        </>
      )}

      {related.length > 0 && (
        <>
          <div className="detail-section-title">Related · {related.length}</div>
          {related.map((r) => (
            <div className="link-chip" key={`rel-${r.id}-${r.rel}`} onClick={() => onSelectLink?.(r.id)}>
              <span className="type-dot" style={{ background: colorFor(r.type) }} />
              {r.name}
              <span className="rel">{(r.rel || "").toLowerCase()}</span>
            </div>
          ))}
        </>
      )}

      <div className="detail-section-title">Agentic intelligence</div>
      <AgentButtons onRun={onRunAgent} running={runningAgent} />

      {agentResult && (
        <AgentResult result={agentResult.result} agentType={agentResult.agent_type} />
      )}
    </div>
  );
}
