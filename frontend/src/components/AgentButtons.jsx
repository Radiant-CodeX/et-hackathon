import { Search, ShieldCheck, History } from "lucide-react";

const AGENTS = [
  { type: "rca", label: "Run RCA", sub: "Find recurring root causes", icon: Search, color: "#ff5d6c" },
  { type: "compliance", label: "Check Compliance", sub: "Flag regulatory gaps", icon: ShieldCheck, color: "#f6b73c" },
  { type: "historian", label: "Equipment History", sub: "Build lifetime narrative", icon: History, color: "#16c4b0" },
];

/**
 * The three agent trigger buttons (playbook §7.4, TDD B5).
 * `running` holds the agent_type currently in flight (or null).
 */
export default function AgentButtons({ onRun, running, disabled }) {
  return (
    <div className="agent-buttons" data-testid="agent-buttons">
      {AGENTS.map(({ type, label, sub, icon: Icon, color }) => (
        <button
          key={type}
          className="agent-btn"
          onClick={() => onRun?.(type)}
          disabled={disabled || !!running}
          type="button"
        >
          <span className="agent-icon" style={{ background: `${color}22`, color }}>
            <Icon size={16} />
          </span>
          <span className="agent-meta">
            {running === type ? "Running…" : label}
            <small>{sub}</small>
          </span>
        </button>
      ))}
    </div>
  );
}
