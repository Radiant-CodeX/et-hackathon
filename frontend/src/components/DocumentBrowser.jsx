import { useEffect, useState } from "react";
import { getEntities } from "../api/client";

export default function DocumentBrowser({ onSelect, refreshKey }) {
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getEntities()
      .then(setEntities)
      .catch(() => setEntities([]))
      .finally(() => setLoading(false));
  }, [refreshKey]);

  if (loading) return <div className="loading">Loading entities...</div>;
  if (entities.length === 0)
    return <div className="loading">No entities yet.</div>;

  return (
    <div className="list">
      {entities.map((e) => (
        <div
          key={e.id}
          className="list-item"
          onClick={() => onSelect({ id: e.id, label: e.name, type: e.type })}
        >
          <span className={`dot type-${e.type}`} />
          <span style={{ flex: 1 }}>{e.name}</span>
          <span className="badge">{e.type}</span>
        </div>
      ))}
    </div>
  );
}
