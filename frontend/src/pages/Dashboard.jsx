import { useCallback, useEffect, useState } from "react";
import { Boxes, Network, PanelRight } from "lucide-react";
import ikip, { apiState } from "../api/client";
import SearchBar from "../components/SearchBar";
import DocumentBrowser from "../components/DocumentBrowser";
import Graph from "../components/Graph";
import EntityPanel from "../components/EntityPanel";
import ErrorState from "../components/ErrorState";

export default function Dashboard() {
  const [graph, setGraph] = useState({ nodes: [], relationships: [] });
  const [entities, setEntities] = useState([]);
  const [searchResults, setSearchResults] = useState(null);

  const [selectedId, setSelectedId] = useState(null);
  const [entity, setEntity] = useState(null);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const [runningAgent, setRunningAgent] = useState(null);
  const [agentResult, setAgentResult] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState("unknown");

  // Initial load: graph + entity list.
  const loadAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [g, e] = await Promise.all([ikip.getGraph(), ikip.getEntities()]);
      setGraph(g);
      setEntities(e);
      setMode(apiState.mode);
    } catch (err) {
      setError("Could not load knowledge graph.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  // Select an entity → fetch its detail + reset any prior agent output.
  const selectEntity = useCallback(async (id) => {
    if (!id) return;
    setSelectedId(id);
    setAgentResult(null);
    setDetailLoading(true);
    try {
      const data = await ikip.getEntity(id);
      setEntity(data.entity);
      setDetail({ backlinks: data.backlinks, related: data.related });
      setMode(apiState.mode);
    } catch (err) {
      setEntity({ id, name: id, type: "Equipment", metadata: {} });
      setDetail(null);
    } finally {
      setDetailLoading(false);
    }
  }, []);

  const handleSearch = useCallback(
    async (q) => {
      if (!q) {
        setSearchResults(null);
        return;
      }
      const results = await ikip.search(q);
      setSearchResults(results);
      setMode(apiState.mode);
    },
    []
  );

  const runAgent = useCallback(
    async (agentType) => {
      if (!selectedId) return;
      setRunningAgent(agentType);
      setAgentResult(null);
      try {
        const res = await ikip.runAgent(agentType, selectedId);
        setAgentResult(res);
        setMode(apiState.mode);
      } finally {
        setRunningAgent(null);
      }
    },
    [selectedId]
  );

  return (
    <div className="app">
      {/* Top bar */}
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <Network size={17} />
          </div>
          <div className="brand-text">
            <h1>Industrial Knowledge Intelligence</h1>
            <p>Unified Asset &amp; Operations Brain</p>
          </div>
        </div>
        <div className="spacer" />
        <div className={`status-pill ${mode === "live" ? "live" : "mock"}`}>
          <span className="dot" />
          {mode === "live" ? "Live backend" : "Demo data"}
        </div>
      </header>

      {/* Three-panel workspace */}
      <div className="workspace">
        {/* LEFT */}
        <aside className="panel left" data-testid="left-sidebar">
          <SearchBar onSearch={handleSearch} />
          <div className="panel-header">
            <Boxes size={14} /> Entities
            <span className="count">{entities.length}</span>
          </div>
          {error ? (
            <ErrorState message={error} onRetry={loadAll} />
          ) : (
            <DocumentBrowser
              entities={entities}
              searchResults={searchResults}
              activeId={selectedId}
              loading={loading}
              onSelect={selectEntity}
            />
          )}
        </aside>

        {/* CENTER */}
        <main className="panel center" data-testid="graph-panel">
          <Graph
            nodes={graph.nodes}
            relationships={graph.relationships}
            onNodeClick={(d) => selectEntity(d.id)}
            selectedId={selectedId}
          />
        </main>

        {/* RIGHT */}
        <aside className="panel right" data-testid="entity-panel">
          <div className="panel-header">
            <PanelRight size={14} /> Inspector
          </div>
          <div className="panel-scroll">
            <EntityPanel
              entity={entity}
              detail={detail}
              loading={detailLoading}
              onSelectLink={selectEntity}
              onRunAgent={runAgent}
              runningAgent={runningAgent}
              agentResult={agentResult}
            />
          </div>
        </aside>
      </div>
    </div>
  );
}
