import type { ReactNode } from "react";

export function StatCard({
  label,
  value,
  accent = "text-slate-900",
}: {
  label: string;
  value: ReactNode;
  accent?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className={`mt-1 text-2xl font-semibold ${accent}`}>{value}</p>
    </div>
  );
}

const STATUS_STYLES: Record<string, string> = {
  queued: "bg-slate-100 text-slate-700",
  scheduled: "bg-sky-100 text-sky-700",
  claimed: "bg-amber-100 text-amber-700",
  running: "bg-blue-100 text-blue-700",
  completed: "bg-emerald-100 text-emerald-700",
  failed: "bg-red-100 text-red-700",
  retrying: "bg-orange-100 text-orange-700",
  dead_letter: "bg-rose-200 text-rose-800",
  cancelled: "bg-slate-200 text-slate-600",
  active: "bg-emerald-100 text-emerald-700",
  idle: "bg-slate-100 text-slate-600",
  draining: "bg-amber-100 text-amber-700",
  crashed: "bg-red-100 text-red-700",
  stopped: "bg-slate-200 text-slate-600",
};

export function StatusBadge({ status }: { status: string }) {
  const style = STATUS_STYLES[status] ?? "bg-slate-100 text-slate-700";
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${style}`}>
      {status.replace("_", " ")}
    </span>
  );
}

export function Card({ title, action, children }: { title?: string; action?: ReactNode; children: ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      {title && (
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3">
          <h3 className="text-sm font-semibold text-slate-800">{title}</h3>
          {action}
        </div>
      )}
      <div className="p-5">{children}</div>
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return <p className="py-8 text-center text-sm text-slate-500">{message}</p>;
}
