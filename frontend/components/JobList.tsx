import type { JobPost } from "@/lib/api";
import JobCard from "./JobCard";

export default function JobList({ jobs }: { jobs: JobPost[] }) {
  if (!jobs.length) return <p className="text-sm text-slate-500">No jobs yet.</p>;
  return (
    <div className="grid gap-4">
      {jobs.map((j) => <JobCard key={j.id} job={j} />)}
    </div>
  );
}
