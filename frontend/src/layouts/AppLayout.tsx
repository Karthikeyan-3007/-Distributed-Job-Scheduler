import { NavLink, Outlet } from "react-router-dom";
import {
  LayoutDashboard,
  ListTodo,
  Layers3,
  FolderKanban,
  Users,
  AlertTriangle,
  LogOut,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";

const NAV_ITEMS = [
  { to: "/", label: "Overview", icon: LayoutDashboard, end: true },
  { to: "/projects", label: "Projects", icon: FolderKanban },
  { to: "/queues", label: "Queues", icon: Layers3 },
  { to: "/jobs", label: "Jobs", icon: ListTodo },
  { to: "/workers", label: "Workers", icon: Users },
  { to: "/dlq", label: "Dead Letter Queue", icon: AlertTriangle },
];

export default function AppLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="flex w-64 flex-col border-r border-slate-200 bg-white">
        <div className="px-5 py-5">
          <p className="text-lg font-bold text-slate-900">JobScheduler</p>
          <p className="text-xs text-slate-500">Distributed job scheduling</p>
        </div>
        <nav className="flex-1 space-y-1 px-3">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive ? "bg-brand-50 text-brand-700" : "text-slate-600 hover:bg-slate-100"
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-slate-100 px-4 py-4">
          <p className="truncate text-xs text-slate-500">{user?.email}</p>
          <button
            onClick={logout}
            className="mt-2 flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-red-600"
          >
            <LogOut size={14} /> Sign out
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto p-6">
        <Outlet />
      </main>
    </div>
  );
}
