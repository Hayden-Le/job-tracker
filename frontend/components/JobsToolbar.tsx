"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

type Props = {
  initialQ?: string;
  initialSource?: string;
  initialSort?: "posted_at_desc" | "posted_at_asc";
  limit?: number;
};

export default function JobsToolbar({
  initialQ = "",
  initialSource = "",
  initialSort = "posted_at_desc",
  limit = 10,
}: Props) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const [q, setQ] = useState(initialQ);
  const [source, setSource] = useState(initialSource);
  const [sort, setSort] = useState(initialSort);

  // Debounce search input (400ms)
  useEffect(() => {
    const t = setTimeout(() => {
      updateQuery({ q, page: "1" });  // reset to page 1 on new search
    }, 400);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q]);

  function updateQuery(next: Record<string, string | undefined>) {
    const sp = new URLSearchParams(searchParams.toString());
    Object.entries(next).forEach(([k, v]) => {
      if (!v) sp.delete(k);
      else sp.set(k, v);
    });
    // Preserve limit
    if (!sp.get("limit")) sp.set("limit", String(limit));
    router.replace(`${pathname}?${sp.toString()}`);
  }

  const [showUpload, setShowUpload] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState("");
  const [keywords, setKeywords] = useState<string[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] || null);
    setStatus("");
  };
  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("cv", file);
    setStatus("Uploading...");
    const res = await fetch("/api/upload-cv", {
      method: "POST",
      body: formData,
    });
    if (res.ok) {
      const data = await res.json();
      setStatus("Upload successful!");
      setKeywords(data.keywords || []);
      setJobs(data.jobs || []);
    } else {
      setStatus("Upload failed.");
      setKeywords([]);
      setJobs([]);
    }
  };

  return (
    <div className="rounded-lg border bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-3 md:flex-row md:items-center">
        <input
          className="w-full rounded border px-3 py-2 text-sm"
          placeholder="Search title, company, location…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <select
          className="rounded border px-3 py-2 text-sm"
          value={source}
          onChange={(e) => {
            setSource(e.target.value);
            updateQuery({ source: e.target.value || undefined, page: "1" });
          }}
        >
          <option value="">All sources</option>
          <option value="seek">seek</option>
          <option value="linkedin">linkedin</option>
          <option value="indeed">indeed</option>
        </select>
        <select
          className="rounded border px-3 py-2 text-sm"
          value={sort}
          onChange={(e) => {
            setSort(e.target.value as any);
            updateQuery({ sort: e.target.value, page: "1" });
          }}
        >
          <option value="posted_at_desc">Newest</option>
          <option value="posted_at_asc">Oldest</option>
        </select>
        <button
          className="rounded bg-slate-900 px-4 py-2 text-sm text-white"
          onClick={() => {
            setQ(""); setSource(""); setSort("posted_at_desc");
            updateQuery({ q: undefined, source: undefined, sort: "posted_at_desc", page: "1" });
          }}
        >
          Clear
        </button>
        <button
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white ml-2 whitespace-nowrap"
          onClick={() => setShowUpload(true)}
        >
          Upload CV
        </button>
      </div>
      {showUpload && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
          <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md relative">
            <button className="absolute top-2 right-2 text-gray-500" onClick={() => setShowUpload(false)}>&times;</button>
            <h2 className="text-xl font-semibold mb-4">Upload your CV (PDF)</h2>
            <input type="file" accept="application/pdf" onChange={handleFileChange} className="mb-4" />
            <button
              onClick={handleUpload}
              disabled={!file}
              className={`w-full py-2 px-4 rounded font-semibold transition-colors duration-200 ${file ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}
            >
              Upload
            </button>
            {status && <p className="mt-3 text-center text-sm text-gray-700">{status}</p>}
            {keywords.length > 0 && (
              <div className="bg-white shadow rounded-lg p-4 mt-4">
                <h3 className="text-lg font-semibold mb-2">Suggested Keywords:</h3>
                <ul className="flex flex-wrap gap-2">
                  {keywords.map((kw, i) => (
                    <li key={i} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">{kw}</li>
                  ))}
                </ul>
              </div>
            )}
            {jobs.length > 0 && (
              <div className="bg-white shadow rounded-lg p-4 mt-4">
                <h3 className="text-lg font-semibold mb-2">Job Results:</h3>
                <ul className="space-y-4">
                  {jobs.map((job, i) => (
                    <li key={i} className="border-b pb-4 last:border-b-0">
                      <div className="font-bold text-base mb-1">{job.job_title}</div>
                      <div className="text-gray-700 mb-1">{job.employer_name} &middot; {job.job_city || job.job_location || job.job_state || ''}, {job.job_country || job.job_location || job.job_state || ''}</div>
                      <a href={job.job_apply_link} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline text-sm">Apply</a>
                      <div className="text-gray-600 text-sm mt-1">{job.job_description?.slice(0, 120)}...</div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
