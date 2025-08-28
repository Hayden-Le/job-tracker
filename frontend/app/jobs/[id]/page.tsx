import { getJob } from "@/lib/api";

export default async function JobDetails({ params }: { params: { id: string } }) {
  const job = await getJob(params.id);

  return (
    <div className="rounded-lg border bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold">{job.title}</h2>
      <p className="mt-1 text-slate-600">{job.company} · {job.location}</p>
      {job.salary_text && <p className="mt-1 text-emerald-700">{job.salary_text}</p>}
      {job.description_snippet && <p className="mt-4 text-slate-800">{job.description_snippet}</p>}
      {job.canonical_url && (
        <a className="mt-4 inline-block text-blue-600 hover:underline" href={job.canonical_url} target="_blank">
          Original posting
        </a>
      )}
    </div>
  );
}
