"use client";

import { useEffect, useMemo, useState } from "react";

type Job = {
  id: number;
  title: string;
  company: string;
  ingested_at?: string; // ISO string from backend
};

export default function HomePage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // read once on mount (safe on client)
  const lastSeenIso = useMemo(
    () => (typeof window !== "undefined" ? window.localStorage.getItem("lastSeen") : null),
    []
  );
  const lastSeenDate = lastSeenIso ? new Date(lastSeenIso) : null;

  useEffect(() => {
    const controller = new AbortController();
    const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    const url = new URL(`${BASE}/jobs`);
    url.searchParams.set("limit", "20");
    url.searchParams.set("offset", "0");

    (async () => {
      try {
        setLoading(true);
        const res = await fetch(url.toString(), { signal: controller.signal, cache: "no-store" });
        if (!res.ok) {
          const text = await res.text();
          throw new Error(`GET /jobs failed: ${res.status} ${text}`);
        }
        const data = (await res.json()) as Job[];
        setJobs(data);
        setError(null);
      } catch (e: any) {
        if (e.name !== "AbortError") setError(e.message ?? "Failed to fetch jobs");
      } finally {
        setLoading(false);
      }
    })();

    // on unmount, record lastSeen
    return () => {
      if (typeof window !== "undefined") {
        window.localStorage.setItem("lastSeen", new Date().toISOString());
      }
      controller.abort();
    };
  }, []);

  return (
    <main style={{ padding: "2rem", maxWidth: 720 }}>
      <h1 style={{ marginBottom: "1rem" }}>Job Tracker</h1>

      {loading && <p>Loading jobs…</p>}
      {error && (
        <p style={{ color: "crimson" }}>
          {error} — check <code>NEXT_PUBLIC_API_URL</code> and backend CORS.
        </p>
      )}

      <ul style={{ lineHeight: 1.8 }}>
        {jobs.map((job) => {
          const isNew =
            lastSeenDate &&
            job.ingested_at &&
            !Number.isNaN(new Date(job.ingested_at).getTime()) &&
            new Date(job.ingested_at).getTime() > lastSeenDate.getTime();

          return (
            <li key={job.id} style={{ fontWeight: isNew ? 700 : 400 }}>
              {job.title} @ {job.company} {isNew ? "• NEW" : ""}
            </li>
          );
        })}
      </ul>
    </main>
  );
}
