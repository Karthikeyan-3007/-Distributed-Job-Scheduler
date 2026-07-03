import { useQuery } from "@tanstack/react-query";
import { WorkerApi } from "../services/resources";
import { Card, EmptyState, StatusBadge } from "../components/ui";

export default function WorkersPage() {
  const { data: workers } = useQuery({
    queryKey: ["workers"],
    queryFn: () => WorkerApi.list().then((r) => r.data.items),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Workers</h1>
        <p className="text-sm text-slate-500">
          Registered worker processes, their concurrency, and last heartbeat.
        </p>
      </div>

      <Card>
        {(workers ?? []).length === 0 ? (
          <EmptyState message="No workers registered. Start one with `python -m app.workers.worker`." />
        ) : (
          <table className="w-full text-sm">
            <thead className="text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="pb-2">Name</th>
                <th className="pb-2">Host</th>
                <th className="pb-2">Concurrency</th>
                <th className="pb-2">Status</th>
                <th className="pb-2">Last heartbeat</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(workers ?? []).map((w) => (
                <tr key={w.id}>
                  <td className="py-2 font-medium text-slate-800">{w.name}</td>
                  <td className="py-2 text-slate-600">{w.hostname}</td>
                  <td className="py-2 text-slate-600">{w.concurrency}</td>
                  <td className="py-2">
                    <StatusBadge status={w.status} />
                  </td>
                  <td className="py-2 text-slate-500">
                    {w.last_heartbeat_at ? new Date(w.last_heartbeat_at).toLocaleTimeString() : "never"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}
