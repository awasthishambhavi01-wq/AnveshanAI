import { useState } from "react";
import { api } from "../api/client";
import { percent } from "../utils/format";

export default function SearchPanel({ selectedIds, readyCount }) {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const run = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;
    setLoading(true);
    setError(null);
    try {
      setResults(await api.search(query.trim(), topK, selectedIds));
    } catch (err) {
      setError(err.message);
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <form onSubmit={run} className="flex flex-wrap items-center gap-2 border-b border-slate-200 bg-white p-3">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by meaning, not just keywords..."
          className="min-w-48 flex-1 rounded-xl border border-slate-300 px-4 py-2.5 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
        />
        <select
          value={topK}
          onChange={(e) => setTopK(Number(e.target.value))}
          className="rounded-xl border border-slate-300 px-3 py-2.5 text-sm"
          aria-label="Number of results"
        >
          {[3, 5, 10, 20].map((n) => (
            <option key={n} value={n}>
              Top {n}
            </option>
          ))}
        </select>
        <button
          type="submit"
          disabled={loading || !query.trim() || readyCount === 0}
          className="rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:bg-slate-300"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {readyCount === 0 && <p className="text-sm text-slate-400">Upload a PDF to search it.</p>}
        {error && <p className="rounded-md bg-red-50 p-3 text-sm text-red-600">{error}</p>}
        {results && results.length === 0 && <p className="text-sm text-slate-400">No matches found.</p>}

        {results?.map((r, i) => (
          <article key={`${r.doc_id}-${r.page}-${i}`} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="mb-2 flex items-center justify-between gap-3 text-xs">
              <span className="truncate font-medium text-slate-700">
                {r.filename} <span className="font-normal text-slate-500">p.{r.page}</span>
              </span>
              <span className="shrink-0 font-medium text-indigo-600">{percent(r.score)}</span>
            </div>
            <div className="mb-3 h-1.5 overflow-hidden rounded-full bg-slate-100">
              <div className="h-full rounded-full bg-indigo-500" style={{ width: percent(r.score) }} />
            </div>
            <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-600">{r.text}</p>
          </article>
        ))}
      </div>
    </div>
  );
}