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
      </div>
    </div>
  );
}
