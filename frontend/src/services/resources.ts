import { api } from "./api";
import type {
  DeadLetterEntry,
  Job,
  JobExecution,
  MetricsOverview,
  Organization,
  Page,
  Project,
  Queue,
  QueueStats,
  User,
  Worker,
} from "../types";

export const AuthApi = {
  login: (email: string, password: string) =>
    api.post<{ access_token: string; refresh_token: string }>("/auth/login", { email, password }),
  register: (email: string, password: string, full_name: string) =>
    api.post<User>("/auth/register", { email, password, full_name }),
  me: () => api.get<User>("/auth/me"),
};

export const OrgApi = {
  list: () => api.get<Organization[]>("/organizations"),
  create: (name: string) => api.post<Organization>("/organizations", { name }),
};

export const ProjectApi = {
  list: (organization_id?: string) =>
    api.get<Page<Project>>("/projects", { params: { organization_id, page_size: 100 } }),
  create: (organization_id: string, name: string, description?: string) =>
    api.post<Project>("/projects", { organization_id, name, description }),
};

export const QueueApi = {
  list: (project_id?: string) =>
    api.get<Page<Queue>>("/queues", { params: { project_id, page_size: 100 } }),
  get: (id: string) => api.get<Queue>(`/queues/${id}`),
  create: (payload: Record<string, unknown>) => api.post<Queue>("/queues", payload),
  update: (id: string, payload: Record<string, unknown>) => api.patch<Queue>(`/queues/${id}`, payload),
  pause: (id: string) => api.post<Queue>(`/queues/${id}/pause`),
  resume: (id: string) => api.post<Queue>(`/queues/${id}/resume`),
  stats: (id: string) => api.get<QueueStats>(`/queues/${id}/stats`),
};

export const JobApi = {
  list: (params: { queue_id?: string; status?: string; page?: number; page_size?: number }) =>
    api.get<Page<Job>>("/jobs", { params }),
  get: (id: string) => api.get<Job>(`/jobs/${id}`),
  create: (payload: Record<string, unknown>) => api.post<Job>("/jobs", payload),
  cancel: (id: string) => api.post<Job>(`/jobs/${id}/cancel`),
  executions: (id: string) => api.get<JobExecution[]>(`/jobs/${id}/executions`),
};

export const WorkerApi = {
  list: () => api.get<Page<Worker>>("/workers", { params: { page_size: 100 } }),
};

export const DlqApi = {
  list: (queue_id?: string) =>
    api.get<Page<DeadLetterEntry>>("/dead-letter-queue", { params: { queue_id, page_size: 100 } }),
  replay: (id: string) => api.post<Job>(`/dead-letter-queue/${id}/replay`),
};

export const MetricsApi = {
  overview: () => api.get<MetricsOverview>("/metrics/overview"),
};
