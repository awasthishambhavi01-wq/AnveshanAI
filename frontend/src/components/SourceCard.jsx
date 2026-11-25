import { percent } from "../utils/format";

export default function SourceCard({ source, highlighted }) {
  return (
    <div
      className={`rounded-lg border p-3 text-sm transition ${
        highlighted ? "border-indigo-400 bg-indigo-50" : "border-slate-200 bg-slate-50"
      }`}
    >
      <div className="mb-1 flex items-center justify-between gap-2 text-xs">
        <span className="flex min-w-0 items-center gap-2">
          <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded bg-indigo-600 font-semibold text-white">
            {source.id}
          </span>
          <span className="truncate font-medium text-slate-700" title={source.filename}>
            {source.filename}
          </span>
          <span className="shrink-0 text-slate-500">p.{source.page}</span>
        </span>
        <span className="shrink-0 text-slate-400">match {percent(source.score)}</span>
      </div>
      <p className="whitespace-pre-wrap text-slate-600">
        {source.snippet}
        {source.snippet.length >= 300 ? "..." : ""}
      </p>
    </div>
  );
}