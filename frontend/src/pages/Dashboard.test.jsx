import { render, screen } from "@testing-library/react";
import { describe, test, expect } from "vitest";
import Dashboard from "./Dashboard";

describe("Dashboard (A1, A2)", () => {
  test("renders dashboard layout with project title", () => {
    render(<Dashboard />);
    expect(screen.getByText(/Industrial Knowledge/i)).toBeInTheDocument();
  });

  test("renders three dashboard panels", () => {
    render(<Dashboard />);
    expect(screen.getByTestId("left-sidebar")).toBeInTheDocument();
    expect(screen.getByTestId("graph-panel")).toBeInTheDocument();
    expect(screen.getByTestId("entity-panel")).toBeInTheDocument();
  });
});
