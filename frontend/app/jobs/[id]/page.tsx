import { getJob } from "@/lib/api";

export default async function JobDetails({ params }: { params: { id: string } }) {
  const job = await getJob(params.id);

  const sections = job.description_sections || {};
  function renderSection(title: string, content: any) {
    if (!content || (Array.isArray(content) && content.length === 0)) return null;
    return (
      <div>
        <h3 className="font-semibold text-base mb-1">{title}</h3>
        {Array.isArray(content) ? (
          <ul className="list-disc pl-5 text-slate-800">
            {content.map((item: string, idx: number) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="text-slate-800 whitespace-pre-line">{content}</p>
        )}
      </div>
    );
  }
  return (
    <div className="rounded-lg border bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold">{job.title}</h2>
      <p className="mt-1 text-slate-600">{job.company} · {job.location}</p>
      {job.salary_text && <p className="mt-1 text-emerald-700">{job.salary_text}</p>}
      {/* Show structured sections if available, else fallback to snippet */}
      {Object.keys(sections).length > 0 ? (
        <div className="mt-4 grid gap-4">
          {renderSection("Responsibilities", sections.Responsibilities)}
          {renderSection("Requirements", sections.Requirements)}
          {renderSection("Nice To Haves", sections.NiceToHaves)}
          {renderSection("Benefits", sections.Benefits)}
        </div>
      ) : (
        job.description_snippet && <p className="mt-4 text-slate-800">{job.description_snippet}</p>
      )}
      {job.canonical_url && (
        <a className="mt-4 inline-block text-blue-600 hover:underline" href={job.canonical_url} target="_blank">
          Original posting
        </a>
      )}
    </div>
  );
}
