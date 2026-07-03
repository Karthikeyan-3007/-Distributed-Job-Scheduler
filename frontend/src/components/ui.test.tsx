import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatCard, StatusBadge } from "../components/ui";

describe("StatCard", () => {
  it("renders label and value", () => {
    render(<StatCard label="Total Jobs" value={42} />);
    expect(screen.getByText("Total Jobs")).toBeInTheDocument();
    expect(screen.getByText("42")).toBeInTheDocument();
  });
});

describe("StatusBadge", () => {
  it("renders a readable status label", () => {
    render(<StatusBadge status="dead_letter" />);
    expect(screen.getByText("dead letter")).toBeInTheDocument();
  });

  it("falls back gracefully for unknown statuses", () => {
    render(<StatusBadge status="unknown_status" />);
    expect(screen.getByText("unknown status")).toBeInTheDocument();
  });
});
