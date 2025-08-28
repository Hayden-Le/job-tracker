import { listJobs, getStats } from "@/lib/api";
import JobList from "@/components/JobList";
import JobsToolbar from "@/components/JobsToolbar";
import Link from "next/link";
import { revalidatePath } from "next/cache";

type SP = { [key: string]: string | string[] | undefined };

export default async function Page({ searchParams }: { searchParams: SP }) {
  const q       = typeof searchParams.q === "string" ? searchParams.q : undefined;
  const source  = typeof searchParams.source === "string" ? searchParams.source : undefined;
  const sort    = (typeof searchParams.sort === "string" ? searchParams.sort : "posted_at_desc") as "posted_at_desc" | "posted_at_asc";
  const pageStr = typeof searchParams.page === "string" ? searchParams.page : "1";
  const limitStr= typeof searchParams.limit === "string" ? searchParams.limit : "10";

  const page  = Math.max(1, parseInt(pageStr || "1", 10));
  const limit = Math.min(100, Math.max(1, parseInt(limitStr || "10", 10)));

  const [jobs, stats] = await Promise.all([
  listJobs({ q, source, sort, page, limit }),
  getStats()
  ]);

  // server action to refresh after create
  async function refresh() {
    "use server";
    revalidatePath("/");
  }

  // --- pagination helpers (simple page-based) ---
  const hasPrev = page > 1;
  const hasNext = jobs.length === limit;

  function buildHref(nextPage: number) {
    const sp = new URLSearchParams();
    if (q) sp.set("q", q);
    if (source) sp.set("source", source);
    if (sort) sp.set("sort", sort);
    sp.set("page", String(nextPage));
    sp.set("limit", String(limit));
    return `/?${sp.toString()}`;
  }

  return (
    <div className="grid gap-6">
      <JobsToolbar
        initialQ={q || ""}
        initialSource={source || ""}
        initialSort={sort}
        limit={limit}
      />

      <div className="rounded-lg border bg-white p-3 text-sm text-slate-700">
        <div>Active jobs: <b>{stats.total_active}</b></div>
        <div className="mt-1 flex gap-4 flex-wrap">
          {stats.per_source.map(s => (
            <span key={s.source}>
              {s.source ?? "(unknown)"}: {s.active_count} • last: {s.last_seen ? new Date(s.last_seen).toLocaleString() : "—"}
            </span>
          ))}
        </div>
      </div>

      <JobList jobs={jobs} />

      <div className="flex items-center justify-between">
        <div className="text-sm text-slate-500">
          Page {page}{hasNext ? "" : " (last page)"}
        </div>
        <div className="flex gap-2">
          {hasPrev && (
            <Link href={buildHref(page - 1)} className="rounded border bg-white px-3 py-1.5 text-sm">
              ← Prev
            </Link>
          )}
          {hasNext && (
            <Link href={buildHref(page + 1)} className="rounded border bg-white px-3 py-1.5 text-sm">
              Next →
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}
