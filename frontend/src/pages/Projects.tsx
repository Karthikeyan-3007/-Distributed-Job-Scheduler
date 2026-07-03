import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { OrgApi, ProjectApi } from "../services/resources";
import { Card, EmptyState } from "../components/ui";

export default function ProjectsPage() {
  const qc = useQueryClient();
  const [orgName, setOrgName] = useState("");
  const [projectName, setProjectName] = useState("");
  const [selectedOrg, setSelectedOrg] = useState<string>("");

  const { data: orgs } = useQuery({ queryKey: ["orgs"], queryFn: () => OrgApi.list().then((r) => r.data) });
  const { data: projects } = useQuery({
    queryKey: ["projects"],
    queryFn: () => ProjectApi.list().then((r) => r.data.items),
  });

  const createOrg = useMutation({
    mutationFn: () => OrgApi.create(orgName),
    onSuccess: () => {
      setOrgName("");
      qc.invalidateQueries({ queryKey: ["orgs"] });
    },
  });

  const createProject = useMutation({
    mutationFn: () => ProjectApi.create(selectedOrg, projectName),
    onSuccess: () => {
      setProjectName("");
      qc.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Projects</h1>
        <p className="text-sm text-slate-500">Organizations own projects; projects own queues.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="New organization">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              createOrg.mutate();
            }}
            className="flex gap-2"
          >
            <input
              required
              placeholder="Organization name"
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <button className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700">
              Create
            </button>
          </form>
        </Card>

        <Card title="New project">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (selectedOrg) createProject.mutate();
            }}
            className="flex gap-2"
          >
            <select
              required
              value={selectedOrg}
              onChange={(e) => setSelectedOrg(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="">Select org…</option>
              {(orgs ?? []).map((o) => (
                <option key={o.id} value={o.id}>
                  {o.name}
                </option>
              ))}
            </select>
            <input
              required
              placeholder="Project name"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <button className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700">
              Create
            </button>
          </form>
        </Card>
      </div>

      <Card title="All projects">
        {(projects ?? []).length === 0 ? (
          <EmptyState message="No projects yet. Create an organization, then a project." />
        ) : (
          <table className="w-full text-sm">
            <thead className="text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="pb-2">Name</th>
                <th className="pb-2">Description</th>
                <th className="pb-2">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(projects ?? []).map((p) => (
                <tr key={p.id}>
                  <td className="py-2 font-medium text-slate-800">{p.name}</td>
                  <td className="py-2 text-slate-500">{p.description ?? "—"}</td>
                  <td className="py-2 text-slate-500">{new Date(p.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}
