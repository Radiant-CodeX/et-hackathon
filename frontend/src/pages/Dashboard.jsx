import { useState } from "react";
import Graph from "../components/Graph.jsx";
import SearchBar from "../components/SearchBar.jsx";
import DocumentBrowser from "../components/DocumentBrowser.jsx";
import EntityPanel from "../components/EntityPanel.jsx";
import { ingest } from "../api/client";

export default function Dashboard() {
  const [selected, setSelected] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await ingest(file);
      setRefreshKey((k) => k + 1);
    } catch (err) {
      console.error("Upload failed", err);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  return (
    <div className="app">
      <div className="sidebar">
        <div className="sidebar-header">
          <h1>Knowledge Intelligence</h1>
          <p>Industrial operations brain</p>
        </div>

        <div className="upload-bar">
          <label>
            {uploading ? "Ingesting..." : "Upload a document"}
            <input type="file" onChange={handleUpload} disabled={uploading} />
          </label>
        </div>

        <SearchBar onSelect={setSelected} />
        <DocumentBrowser onSelect={setSelected} refreshKey={refreshKey} />
      </div>

      <div className="center">
        <Graph onNodeClick={setSelected} refreshKey={refreshKey} />
      </div>

      <div className="detail">
        {selected ? (
          <EntityPanel entity={selected} />
        ) : (
          <div className="empty">Select an entity to explore</div>
        )}
      </div>
    </div>
  );
}
