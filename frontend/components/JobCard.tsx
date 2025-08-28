import type { JobPost } from "@/lib/api";
import Link from "next/link";

export default function JobCard({ job }: { job: JobPost }) {
  return (
    <div className="rounded-lg border bg-white p-5 shadow-sm transition hover:shadow-md">
      <div className="flex items-start justify-between gap-4">
        <h3 className="text-lg font-semibold">{job.title}</h3>
        <span className="shrink-0 text-xs text-slate-500">
          {new Date(job.posted_at).toLocaleDateString()}
        </span>
      </div>

      <p className="mt-1 text-sm text-slate-600">
        {job.company} · {job.location}
      </p>

      {job.salary_text && (
        <p className="mt-1 text-sm font-medium text-emerald-700">{job.salary_text}</p>
      )}

      {job.description_snippet && (
        <p className="mt-3 line-clamp-2 text-sm text-slate-700">{job.description_snippet}</p>
      )}

      <div className="mt-4 flex gap-4 text-sm">
        {job.canonical_url && (
          <a className="text-blue-600 hover:underline" href={job.canonical_url} target="_blank">
            Original
          </a>
        )}
        <Link className="text-blue-600 hover:underline" href={`/jobs/${job.id}`}>
          Details
        </Link>
      </div>
    </div>
  );
}
