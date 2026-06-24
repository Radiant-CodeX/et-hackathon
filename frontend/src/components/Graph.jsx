import { useEffect, useRef, useState } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import { getGraph } from "../api/client";

const COLORS = {
  Equipment: "#2e5c9e",
  Procedure: "#4a3c8c",
  FailureMode: "#a6432b",
  Supplier: "#0f6e56",
  ComplianceStd: "#9a6410",
  Unknown: "#5f5e5a",
};

const stylesheet = [
  {
    selector: "node",
    style: {
      label: "data(label)",
      "background-color": (ele) => COLORS[ele.data("type")] || COLORS.Unknown,
      color: "#1f2933",
      "font-size": 11,
      "text-valign": "bottom",
      "text-margin-y": 4,
      width: 28,
      height: 28,
    },
  },
  {
    selector: "edge",
    style: {
      width: 1.5,
      "line-color": "#cbd5e1",
      "target-arrow-color": "#cbd5e1",
      "target-arrow-shape": "triangle",
      "curve-style": "bezier",
      label: "data(label)",
      "font-size": 9,
      color: "#94a3b8",
      "text-rotation": "autorotate",
    },
  },
  {
    selector: "node:selected",
    style: { "border-width": 3, "border-color": "#1a2b4a" },
  },
];

export default function Graph({ onNodeClick, refreshKey }) {
  const [elements, setElements] = useState([]);
  const [loading, setLoading] = useState(true);
  const cyRef = useRef(null);

  useEffect(() => {
    setLoading(true);
    getGraph()
      .then((data) => {
        const nodes = (data.nodes || []).map((n) => ({
          data: { id: n.id, label: n.name, type: n.type },
        }));
        const edges = (data.relationships || []).map((r, i) => ({
          data: {
            id: `e${i}`,
            source: r.source,
            target: r.target,
            label: r.type,
          },
        }));
        setElements([...nodes, ...edges]);
      })
      .catch(() => setElements([]))
      .finally(() => setLoading(false));
  }, [refreshKey]);

  if (loading) return <div className="empty">Loading graph...</div>;
  if (elements.length === 0)
    return <div className="empty">No entities yet. Upload a document to begin.</div>;

  return (
    <CytoscapeComponent
      elements={elements}
      style={{ width: "100%", height: "100%" }}
      layout={{ name: "cose", animate: false, nodeRepulsion: 8000 }}
      stylesheet={stylesheet}
      cy={(cy) => {
        cyRef.current = cy;
        cy.removeListener("tap");
        cy.on("tap", "node", (e) => onNodeClick(e.target.data()));
      }}
    />
  );
}
