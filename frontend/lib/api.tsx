export type StatsOut = {
  total_active: number;
  per_source: { source: string; active_count: number; last_seen: string | null }[];
};

export async function getStats(): Promise<StatsOut> {
  const res = await fetch(`${API}/stats`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch stats");
  return res.json();
}

export type JobPost = {
  id: string;
  source: string;
  title: string;
  company: string;
  location: string;
  description_snippet: string | null;
  posted_at: string;
  canonical_url: string | null;
  salary_text: string | null;
  description_sections?: Record<string, string[] | string>;
};

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type ListParams = {
  q?: string;
  source?: string;
  sort?: "posted_at_desc" | "posted_at_asc";
  page?: number;
  limit?: number;
};

export async function listJobs(params: ListParams = {}): Promise<JobPost[]> {
  const qs = new URLSearchParams();
  if (params.q) qs.set("q", params.q);
  if (params.source) qs.set("source", params.source);
  if (params.sort) qs.set("sort", params.sort);
  if (params.page) qs.set("page", String(params.page));
  if (params.limit) qs.set("limit", String(params.limit));

  const res = await fetch(`${API}/jobs?${qs.toString()}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch jobs (${res.status})`);
  return res.json();
}

export async function createJob(payload: Partial<JobPost>) {
  const res = await fetch(`${API}/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to create job");
  return res.json();
}

export async function getJob(id: string): Promise<JobPost> {
  const res = await fetch(`${API}/jobs/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch job");
  return res.json();
}
