import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { JobApi, QueueApi } from "../services/resources";
import { Card, EmptyState, StatusBadge } from "../components/ui";
import type { JobStatus, JobType } from "../types";

const STATUS_OPTIONS: JobStatus[] = [
  "queued",
  "scheduled",
  "claimed",
  "running",
  "completed",
  "failed",
  "retrying",
  "dead_letter",
  "cancelled",
];

export default function JobsPage() {
  const qc = useQueryClient();
  const [queueFilter, setQueueFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [showForm, setShowForm] = useState(false);

  const { data: queues } = useQuery({
    queryKey: ["queues"],
    queryFn: () => QueueApi.list().then((r) => r.data.items),
  });
  const { data: jobs } = useQuery({
    queryKey: ["jobs", queueFilter, statusFilter],
    queryFn: () =>
      JobApi.list({ queue_id: queueFilter || undefined, status: statusFilter || undefined, page_size: 50 }).then(
        (r) => r.data.items,
      ),
  });

  const [form, setForm] = useState({
    queue_id: "",
    name: "default",
    job_type: "immediate" as JobType,
    priority: 0,
    run_at: "",
    cron_expression: "",
  });

  const createJob = useMutation({
    mutationFn: () =>
      JobApi.create({
        queue_id: form.queue_id,
        name: form.name,
        job_type: form.job_type,
        priority: form.priority,
        payload: {},
        run_at: form.run_at ? new Date(form.run_at).toISOString() : undefined,
        cron_expression: form.cron_expression || undefined,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["jobs"] });
      setShowForm(false);
    },
  });

  const cancelJob = useMutation({
    mutationFn: (id: string) => JobApi.cancel(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["jobs"] }),
  });

  const needsRunAt = form.job_type === "delayed" || form.job_type === "scheduled";
  const needsCron = form.job_type === "recurring";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Jobs</h1>
          <p className="text-sm text-slate-500">Submit and track immediate, delayed, scheduled, recurring, and batch jobs.</p>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700"
        >
          {showForm ? "Cancel" : "Submit job"}
        </button>
      </div>

      {showForm && (
        <Card title="Submit a job">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              createJob.mutate();
            }}
            className="grid grid-cols-2 gap-4 md:grid-cols-3"
          >
            <select
              required
              value={form.queue_id}
              onChange={(e) => setForm({ ...form, queue_id: e.target.value })}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="">Select queue…</option>
              {(queues ?? []).map((q) => (
                <option key={q.id} value={q.id}>
                  {q.name}
                </option>
              ))}
            </select>
            <input
              required
              placeholder="Job name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <select
              value={form.job_type}
              onChange={(e) => setForm({ ...form, job_type: e.target.value as JobType })}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="immediate">Immediate</option>
              <option value="delayed">Delayed</option>
              <option value="scheduled">Scheduled</option>
              <option value="recurring">Recurring (cron)</option>
              <option value="batch">Batch</option>
            </select>
            {needsRunAt && (
              <input
                required
                type="datetime-local"
                value={form.run_at}
                onChange={(e) => setForm({ ...form, run_at: e.target.value })}
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            )}
            {needsCron && (
              <input
                required
                placeholder="Cron expression, e.g. */5 * * * *"
                value={form.cron_expression}
                onChange={(e) => setForm({ ...form, cron_expression: e.target.value })}
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            )}
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
            <button className="col-span-full rounded-lg bg-brand-600 py-2 text-sm font-semibold text-white hover:bg-brand-700">
              Submit
            </button>
          </form>
        </Card>
      )}

      <div className="flex gap-3">
        <select
          value={queueFilter}
          onChange={(e) => setQueueFilter(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">All queues</option>
          {(queues ?? []).map((q) => (
            <option key={q.id} value={q.id}>
              {q.name}
            </option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">All statuses</option>
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      <Card>
        {(jobs ?? []).length === 0 ? (
          <EmptyState message="No jobs match these filters." />
        ) : (
          <table className="w-full text-sm">
            <thead className="text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="pb-2">Name</th>
                <th className="pb-2">Type</th>
                <th className="pb-2">Status</th>
                <th className="pb-2">Retries</th>
                <th className="pb-2">Created</th>
                <th className="pb-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(jobs ?? []).map((j) => (
                <tr key={j.id}>
                  <td className="py-2 font-medium text-slate-800">{j.name}</td>
                  <td className="py-2 text-slate-600">{j.job_type}</td>
                  <td className="py-2">
                    <StatusBadge status={j.status} />
                  </td>
                  <td className="py-2 text-slate-600">
                    {j.retry_count}/{j.max_retries}
                  </td>
                  <td className="py-2 text-slate-500">{new Date(j.created_at).toLocaleString()}</td>
                  <td className="py-2 text-right">
                    {!["completed", "dead_letter", "cancelled"].includes(j.status) && (
                      <button
                        onClick={() => cancelJob.mutate(j.id)}
                        className="text-xs font-medium text-red-600 hover:underline"
                      >
                        Cancel
                      </button>
                    )}
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
