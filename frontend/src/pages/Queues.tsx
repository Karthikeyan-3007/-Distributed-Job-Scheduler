import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ProjectApi, QueueApi } from "../services/resources";
import { Card, EmptyState, StatusBadge } from "../components/ui";

export default function QueuesPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const { data: projects } = useQuery({
    queryKey: ["projects"],
    queryFn: () => ProjectApi.list().then((r) => r.data.items),
  });
  const { data: queues } = useQuery({
    queryKey: ["queues"],
    queryFn: () => QueueApi.list().then((r) => r.data.items),
  });

  const [form, setForm] = useState({
    project_id: "",
    name: "",
    priority: 0,
    concurrency_limit: 5,
    max_retries: 3,
    strategy: "exponential",
  });

  const createQueue = useMutation({
    mutationFn: () =>
      QueueApi.create({
        project_id: form.project_id,
        name: form.name,
        priority: form.priority,
        concurrency_limit: form.concurrency_limit,
        max_retries: form.max_retries,
        retry_policy: { strategy: form.strategy, base_delay_seconds: 5, max_delay_seconds: 300 },
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["queues"] });
      setShowForm(false);
    },
  });

  const togglePause = useMutation({
    mutationFn: ({ id, pause }: { id: string; pause: boolean }) =>
      pause ? QueueApi.pause(id) : QueueApi.resume(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["queues"] }),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Queues</h1>
          <p className="text-sm text-slate-500">Priority, concurrency, retries, and pause/resume control.</p>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700"
        >
          {showForm ? "Cancel" : "New queue"}
        </button>
      </div>

      {showForm && (
        <Card title="Create queue">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              createQueue.mutate();
            }}
            className="grid grid-cols-2 gap-4 md:grid-cols-3"
          >
            <select
              required
              value={form.project_id}
              onChange={(e) => setForm({ ...form, project_id: e.target.value })}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="">Select project…</option>
              {(projects ?? []).map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
            <input
              required
              placeholder="Queue name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <select
              value={form.strategy}
              onChange={(e) => setForm({ ...form, strategy: e.target.value })}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="fixed">Fixed delay</option>
              <option value="linear">Linear backoff</option>
              <option value="exponential">Exponential backoff</option>
            </select>
            <label className="flex flex-col text-xs text-slate-500">
              Priority (0-100)
              <input
                type="number"
                min={0}
                max={100}
                value={form.priority}
                onChange={(e) => setForm({ ...form, priority: Number(e.target.value) })}
                className="mt-1 rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-800"
              />
            </label>
            <label className="flex flex-col text-xs text-slate-500">
              Concurrency limit
              <input
                type="number"
                min={1}
                value={form.concurrency_limit}
                onChange={(e) => setForm({ ...form, concurrency_limit: Number(e.target.value) })}
                className="mt-1 rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-800"
              />
            </label>
            <label className="flex flex-col text-xs text-slate-500">
              Max retries
              <input
                type="number"
                min={0}
                value={form.max_retries}
                onChange={(e) => setForm({ ...form, max_retries: Number(e.target.value) })}
                className="mt-1 rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-800"
              />
            </label>
            <button className="col-span-full rounded-lg bg-brand-600 py-2 text-sm font-semibold text-white hover:bg-brand-700">
              Create queue
            </button>
          </form>
        </Card>
      )}

      <Card>
        {(queues ?? []).length === 0 ? (
          <EmptyState message="No queues yet. Create a project first, then a queue." />
        ) : (
          <table className="w-full text-sm">
            <thead className="text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="pb-2">Name</th>
                <th className="pb-2">Priority</th>
                <th className="pb-2">Concurrency</th>
                <th className="pb-2">Retry strategy</th>
                <th className="pb-2">Status</th>
                <th className="pb-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(queues ?? []).map((q) => (
                <tr key={q.id}>
                  <td className="py-2 font-medium text-slate-800">{q.name}</td>
                  <td className="py-2 text-slate-600">{q.priority}</td>
                  <td className="py-2 text-slate-600">{q.concurrency_limit}</td>
                  <td className="py-2 text-slate-600">{q.retry_policy?.strategy ?? "—"}</td>
                  <td className="py-2">
                    <StatusBadge status={q.is_paused ? "stopped" : "active"} />
                  </td>
                  <td className="py-2 text-right">
                    <button
                      onClick={() => togglePause.mutate({ id: q.id, pause: !q.is_paused })}
                      className="text-xs font-medium text-brand-600 hover:underline"
                    >
                      {q.is_paused ? "Resume" : "Pause"}
                    </button>
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
