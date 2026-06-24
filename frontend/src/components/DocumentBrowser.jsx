import { colorFor, TYPE_LABELS } from "./nodeTypes";
import Loading from "./Loading";

/**
 * Left-sidebar list. Doubles as the document/entity browser and the
 * search-results view. When `searchResults` is non-null it shows the
 * scored results; otherwise it lists all entities.
 */
export default function DocumentBrowser({
  entities = [],
  searchResults = null,
  activeId,
  loading,
  onSelect,
}) {
  if (loading) return <Loading label="Loading entities…" />;

  const showingSearch = searchResults !== null;
  const items = showingSearch ? searchResults : entities;

  return (
    <div className="panel-scroll" data-testid="document-browser">
      <div className="list-section-label">
        {showingSearch ? `Results · ${items.length}` : "All entities"}
      </div>

      {items.length === 0 && (
        <div className="empty-note">
          {showingSearch ? "No matches found." : "No entities yet."}
        </div>
      )}

      {items.map((e) => (
        <div
          key={e.id}
          className={`entity-row${e.id === activeId ? " active" : ""}`}
          onClick={() => onSelect?.(e.id)}
          role="button"
          tabIndex={0}
          onKeyDown={(ev) => ev.key === "Enter" && onSelect?.(e.id)}
        >
          <span className="type-dot" style={{ background: colorFor(e.type) }} />
          <span className="name">{e.name}</span>
          {showingSearch && typeof e.score === "number" ? (
            <span className="search-score">{e.score.toFixed(2)}</span>
          ) : (
            <span className="type-tag">{TYPE_LABELS[e.type] || e.type}</span>
          )}
        </div>
      ))}
    </div>
  );
}
