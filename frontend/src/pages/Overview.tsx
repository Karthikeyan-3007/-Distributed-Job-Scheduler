import { useQuery } from "@tanstack/react-query";
import { MetricsApi, WorkerApi } from "../services/resources";
import { Card, StatCard, StatusBadge } from "../components/ui";
import { JobStatusPieChart } from "../charts/JobStatusPieChart";

export default function OverviewPage() {
  const { data: metrics } = useQuery({
    queryKey: ["metrics-overview"],
    queryFn: () => MetricsApi.overview().then((r) => r.data),
  });
  const { data: workers } = useQuery({
    queryKey: ["workers-overview"],
    queryFn: () => WorkerApi.list().then((r) => r.data.items),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Overview</h1>
        <p className="text-sm text-slate-500">Live system health across all queues and workers.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Total Jobs" value={metrics?.total_jobs ?? "—"} />
        <StatCard label="Running" value={metrics?.running ?? "—"} accent="text-blue-600" />
        <StatCard label="Failure Rate" value={metrics ? `${(metrics.failure_rate * 100).toFixed(1)}%` : "—"} accent="text-red-600" />
        <StatCard label="Active Workers" value={metrics?.active_workers ?? "—"} accent="text-emerald-600" />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Job status breakdown">
          {metrics ? <JobStatusPieChart metrics={metrics} /> : null}
        </Card>

        <Card title="Worker health">
          <div className="space-y-3">
            {(workers ?? []).slice(0, 8).map((w) => (
              <div key={w.id} className="flex items-center justify-between text-sm">
                <div>
                  <p className="font-medium text-slate-800">{w.name}</p>
                  <p className="text-xs text-slate-500">{w.hostname}</p>
                </div>
                <StatusBadge status={w.status} />
              </div>
            ))}
            {(workers ?? []).length === 0 && (
              <p className="py-8 text-center text-sm text-slate-500">
                No workers registered yet. Start one with{" "}
                <code className="rounded bg-slate-100 px-1 py-0.5">python -m app.workers.worker</code>.
              </p>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
