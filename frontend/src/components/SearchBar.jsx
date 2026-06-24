import { useState, useEffect } from "react";
import { search } from "../api/client";

export default function SearchBar({ onSelect }) {
  const [q, setQ] = useState("");
  const [results, setResults] = useState([]);

  useEffect(() => {
    if (!q.trim()) {
      setResults([]);
      return;
    }
    const t = setTimeout(() => {
      search(q).then(setResults).catch(() => setResults([]));
    }, 250);
    return () => clearTimeout(t);
  }, [q]);

  return (
    <div className="search-box">
      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search equipment, procedures..."
      />
      {results.length > 0 && (
        <div style={{ marginTop: 8 }}>
          {results.map((r) => (
            <div
              key={r.id}
              className="list-item"
              onClick={() => onSelect({ id: r.id, label: r.name, type: r.type })}
            >
              <span className={`dot type-${r.type}`} />
              {r.name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
