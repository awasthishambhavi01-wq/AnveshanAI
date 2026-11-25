import { useState } from "react";
import { formatDate } from "../utils/format";

const BADGE = {
  ready: "bg-emerald-100 text-emerald-700",
  processing: "bg-amber-100 text-amber-700",
  failed: "bg-red-100 text-red-700",
};

export default function DocumentList({
  documents,
  selectedIds,
  loading,
  error,
  onToggle,
  onDelete,
  onClearSelection,
  onRefresh,
}) {
  const [deletingId, setDeletingId] = useState(null);

  const handleDelete = async (doc) => {
    if (!window.confirm(`Delete "${doc.filename}"? Its indexed content will be removed.`)) return;
    setDeletingId(doc.id);
    await onDelete(doc.id);
    setDeletingId(null);
  };

  return (
    <section className="flex min-h-0 flex-1 flex-col">
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-700">Documents ({documents.length})</h2>
        <div className="flex gap-3 text-xs">
          {selectedIds.length > 0 && (
            <button onClick={onClearSelection} className="text-indigo-600 hover:underline">
              Clear selection
            </button>
          )}
          <button onClick={onRefresh} className="text-slate-500 hover:text-slate-700">
            Refresh
          </button>
        </div>
      </div>

      <p className="mb-3 text-xs text-slate-500">
        {selectedIds.length > 0
          ? `Using ${selectedIds.length} selected document${selectedIds.length > 1 ? "s" : ""}.`
          : "Nothing selected: all ready documents are used."}
      </p>

      {error && <p className="mb-2 rounded-md bg-red-50 p-2 text-xs text-red-600">{error}</p>}
      {loading && <p className="text-sm text-slate-400">Loading...</p>}
      {!loading && documents.length === 0 && !error && (
        <p className="text-sm text-slate-400">No documents yet. Upload a PDF to begin.</p>
      )}

      <ul className="space-y-2 overflow-y-auto">
        {documents.map((doc) => {
          const ready = doc.status === "ready";
          const selected = selectedIds.includes(doc.id);
          return (
            <li
              key={doc.id}
              className={`rounded-lg border p-3 text-sm ${
                selected ? "border-indigo-300 bg-indigo-50" : "border-slate-200 bg-white"
              }`}
            >
              <div className="flex items-start gap-2">
                <input
                  type="checkbox"
                  checked={selected}
                  disabled={!ready}
                  onChange={() => onToggle(doc.id)}
                  className="mt-1 h-4 w-4 accent-indigo-600 disabled:opacity-40"
                  aria-label={`Select ${doc.filename}`}
                />
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium text-slate-800" title={doc.filename}>
                    {doc.filename}
                  </p>
                  <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                    <span className={`rounded-full px-2 py-0.5 font-medium ${BADGE[doc.status] || BADGE.processing}`}>
                      {doc.status}
                    </span>
                    {ready && <span>{doc.pages} pages</span>}
                    <span>{formatDate(doc.created_at)}</span>
                  </div>
                  {doc.status === "failed" && doc.error && (
                    <p className="mt-1 text-xs text-red-600">{doc.error}</p>
                  )}
                </div>
                <button
                  onClick={() => handleDelete(doc)}
                  disabled={deletingId === doc.id}
                  className="text-xs text-slate-400 hover:text-red-600 disabled:opacity-50"
                >
                  {deletingId === doc.id ? "..." : "Delete"}
                </button>
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}