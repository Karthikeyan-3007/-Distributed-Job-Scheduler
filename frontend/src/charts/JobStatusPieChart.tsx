import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import type { MetricsOverview } from "../types";

const COLORS: Record<string, string> = {
  Queued: "#94a3b8",
  Running: "#3b82f6",
  Completed: "#10b981",
  Failed: "#ef4444",
  "Dead letter": "#be123c",
};

export function JobStatusPieChart({ metrics }: { metrics: MetricsOverview }) {
  const data = [
    { name: "Queued", value: metrics.queued },
    { name: "Running", value: metrics.running },
    { name: "Completed", value: metrics.completed },
    { name: "Failed", value: metrics.failed },
    { name: "Dead letter", value: metrics.dead_letter },
  ].filter((d) => d.value > 0);

  if (data.length === 0) {
    return <p className="py-10 text-center text-sm text-slate-500">No job data yet — submit a job to see it here.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="name" innerRadius={60} outerRadius={95} paddingAngle={2}>
          {data.map((entry) => (
            <Cell key={entry.name} fill={COLORS[entry.name] ?? "#6366f1"} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
