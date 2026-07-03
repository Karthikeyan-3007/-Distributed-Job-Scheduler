import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { DlqApi } from "../services/resources";
import { Card, EmptyState } from "../components/ui";

export default function DeadLetterQueuePage() {
  const qc = useQueryClient();
  const { data: entries } = useQuery({
    queryKey: ["dlq"],
    queryFn: () => DlqApi.list().then((r) => r.data.items),
  });

  const replay = useMutation({
    mutationFn: (id: string) => DlqApi.replay(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["dlq"] });
      qc.invalidateQueries({ queryKey: ["jobs"] });
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Dead Letter Queue</h1>
        <p className="text-sm text-slate-500">Jobs that exhausted their retry budget. Inspect and replay them.</p>
      </div>

      <Card>
        {(entries ?? []).length === 0 ? (
          <EmptyState message="Nothing in the dead letter queue right now — good sign." />
        ) : (
          <div className="divide-y divide-slate-100">
            {(entries ?? []).map((e) => (
              <div key={e.id} className="flex items-start justify-between py-3">
                <div className="flex-1 pr-4">
                  <p className="text-sm font-medium text-slate-800">Job {e.job_id.slice(0, 8)}</p>
                  <p className="mt-1 text-xs text-slate-500">{e.reason}</p>
                  <p className="mt-1 text-xs text-slate-400">
                    Failed {new Date(e.created_at).toLocaleString()}
                    {e.replayed && " · already replayed"}
                  </p>
                </div>
                <button
                  disabled={e.replayed}
                  onClick={() => replay.mutate(e.id)}
                  className="shrink-0 rounded-lg border border-brand-200 px-3 py-1.5 text-xs font-semibold text-brand-700 hover:bg-brand-50 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Replay
                </button>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
