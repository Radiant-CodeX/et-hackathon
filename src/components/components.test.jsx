import { render, screen, fireEvent } from "@testing-library/react";
import { describe, test, expect, vi } from "vitest";
import Graph from "./Graph";
import SearchBar from "./SearchBar";
import EntityPanel from "./EntityPanel";
import AgentResult from "./AgentResult";

describe("Graph (A4)", () => {
  test("renders graph component with mock elements without crashing", () => {
    const nodes = [{ id: "Pump-01", name: "Pump-01", type: "Equipment" }];
    render(<Graph nodes={nodes} relationships={[]} onNodeClick={() => {}} />);
    expect(screen.getByTestId("cytoscape-host")).toBeInTheDocument();
  });
});

describe("SearchBar (A5)", () => {
  test("user can type a search query", () => {
    render(<SearchBar onSearch={() => {}} />);
    const input = screen.getByPlaceholderText(/search/i);
    fireEvent.change(input, { target: { value: "Pump-01" } });
    expect(input.value).toBe("Pump-01");
  });

  test("submitting calls onSearch with the query", () => {
    const onSearch = vi.fn();
    render(<SearchBar onSearch={onSearch} />);
    fireEvent.change(screen.getByPlaceholderText(/search/i), {
      target: { value: "Pump-01" },
    });
    fireEvent.click(screen.getByRole("button", { name: /run search/i }));
    expect(onSearch).toHaveBeenCalledWith("Pump-01");
  });
});

describe("EntityPanel (A6)", () => {
  test("displays selected entity details", () => {
    const entity = { id: "Pump-01", name: "Pump-01", type: "Equipment" };
    render(<EntityPanel entity={entity} />);
    expect(screen.getByText("Pump-01")).toBeInTheDocument();
    // exact match avoids colliding with the "Equipment History" agent button
    expect(screen.getByText("Equipment")).toBeInTheDocument();
  });

  test("shows empty state when no entity selected", () => {
    render(<EntityPanel entity={null} />);
    expect(screen.getByTestId("entity-empty")).toBeInTheDocument();
  });
});

describe("AgentResult (A7)", () => {
  const mockAgentResult = {
    summary: "Bearing failure pattern detected.",
    findings: [
      { text: "Pump-01 has repeated bearing failure.", confidence: 0.86, citations: ["doc-01:chunk-2"] },
    ],
    recommendation: "Review supplier qualification.",
  };

  test("renders summary, confidence and citation", () => {
    render(<AgentResult result={mockAgentResult} agentType="rca" />);
    expect(screen.getByText(/Bearing failure pattern/i)).toBeInTheDocument();
    expect(screen.getByText(/0.86/)).toBeInTheDocument();
    expect(screen.getByText(/doc-01:chunk-2/)).toBeInTheDocument();
    expect(screen.getByText(/Review supplier qualification/i)).toBeInTheDocument();
  });
});
