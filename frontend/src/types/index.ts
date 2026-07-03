export type JobStatus =
  | "queued"
  | "scheduled"
  | "claimed"
  | "running"
  | "completed"
  | "failed"
  | "retrying"
  | "dead_letter"
  | "cancelled";

export type JobType = "immediate" | "delayed" | "scheduled" | "recurring" | "batch";

export type RetryStrategy = "fixed" | "linear" | "exponential";

export type WorkerStatus = "active" | "idle" | "draining" | "crashed" | "stopped";

export interface Organization {
  id: string;
  name: string;
  owner_id: string;
  created_at: string;
}

export interface Project {
  id: string;
  organization_id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface RetryPolicy {
  id: string;
  strategy: RetryStrategy;
  base_delay_seconds: number;
  max_delay_seconds: number;
}

export interface Queue {
  id: string;
  project_id: string;
  name: string;
  priority: number;
  concurrency_limit: number;
  max_retries: number;
  timeout_seconds: number;
  visibility_timeout_seconds: number;
  is_paused: boolean;
  created_at: string;
  retry_policy: RetryPolicy | null;
}

export interface QueueStats {
  queue_id: string;
  queued: number;
  running: number;
  completed: number;
  failed: number;
  dead_letter: number;
  avg_duration_ms: number | null;
  throughput_last_hour: number;
}

export interface Job {
  id: string;
  queue_id: string;
  name: string;
  job_type: JobType;
  status: JobStatus;
  payload: Record<string, unknown>;
  priority: number;
  run_at: string | null;
  cron_expression: string | null;
  max_retries: number;
  retry_count: number;
  created_at: string;
  updated_at: string;
}

export interface JobExecution {
  id: string;
  job_id: string;
  worker_id: string | null;
  attempt_number: number;
  status: "running" | "succeeded" | "failed" | "timed_out";
  started_at: string | null;
  completed_at: string | null;
  duration_ms: number | null;
  error_message: string | null;
}

export interface Worker {
  id: string;
  name: string;
  hostname: string;
  status: WorkerStatus;
  concurrency: number;
  last_heartbeat_at: string | null;
}

export interface DeadLetterEntry {
  id: string;
  job_id: string;
  queue_id: string;
  reason: string;
  payload_snapshot: Record<string, unknown>;
  replayed: boolean;
  created_at: string;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface MetricsOverview {
  total_jobs: number;
  queued: number;
  running: number;
  completed: number;
  failed: number;
  dead_letter: number;
  failure_rate: number;
  active_workers: number;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "admin" | "member";
  is_active: boolean;
}
