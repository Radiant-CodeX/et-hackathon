import { Sparkles } from "lucide-react";

const AGENT_NAMES = {
  rca: "Root Cause Analysis",
  compliance: "Compliance Check",
  historian: "Equipment Historian",
};

/**
 * Structured agent-result display (TDD A7 / B5).
 * Renders summary, findings (each with confidence + citations),
 * and the recommendation.
 */
export default function AgentResult({ result, agentType }) {
  if (!result) return null;
  const { summary, findings = [], recommendation } = result;

  return (
    <div className="agent-result" data-testid="agent-result">
      <div className="agent-result-head">
        <Sparkles size={15} color="#4f8cff" />
        <span className="label">{AGENT_NAMES[agentType] || "Agent Result"}</span>
      </div>

      <div className="agent-result-body">
        {summary && <p className="agent-summary">{summary}</p>}

        {findings.map((f, i) => {
          const pct = Math.round((f.confidence ?? 0) * 100);
          return (
            <div className="finding" key={i}>
              <p className="finding-text">{f.text}</p>
              <div className="confidence">
                <div className="bar">
                  <span style={{ width: `${pct}%` }} />
                </div>
                <span className="val">{(f.confidence ?? 0).toFixed(2)}</span>
              </div>
              {f.citations?.length > 0 && (
                <div className="citations">
                  {f.citations.map((c, j) => (
                    <span className="citation" key={j}>
                      {c}
                    </span>
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {recommendation && (
          <div className="recommendation">
            <strong>Recommendation</strong>
            {recommendation}
          </div>
        )}
      </div>
    </div>
  );
}
