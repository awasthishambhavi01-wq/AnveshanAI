import { useRef, useState } from "react";

const FEEDBACK_STYLE = {
  success: "text-emerald-700",
  info: "text-slate-600",
  error: "text-red-600",
};

export default function UploadPanel({ onUpload, uploading, feedback, onDismiss }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  const handleFiles = (fileList) => {
    const files = Array.from(fileList || []);
    if (files.length) onUpload(files);
  };

  return (
    <section>
      <div
        onClick={() => !uploading && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          if (!uploading) handleFiles(e.dataTransfer.files);
        }}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-4 py-6 text-center transition ${
          dragging ? "border-indigo-400 bg-indigo-50" : "border-slate-300 hover:border-indigo-300 hover:bg-slate-50"
        } ${uploading ? "cursor-wait opacity-70" : ""}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          multiple
          className="hidden"
          onChange={(e) => {
            handleFiles(e.target.files);
            e.target.value = ""; // allow selecting the same file again
          }}
        />
        {uploading ? (
          <>
            <div className="mb-2 h-6 w-6 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" />
            <p className="text-sm font-medium text-slate-700">Uploading and indexing...</p>
            <p className="mt-1 text-xs text-slate-500">Large PDFs can take a minute.</p>
          </>
        ) : (
          <>
            <p className="text-sm font-medium text-slate-700">Drop PDFs here or click to browse</p>
            <p className="mt-1 text-xs text-slate-500">Text-based PDFs only, up to 20 MB each</p>
          </>
        )}
      </div>

      {feedback.length > 0 && (
        <div className="mt-3 rounded-lg bg-slate-50 p-3 text-xs">
          <ul className="space-y-1">
            {feedback.map((f, i) => (
              <li key={i} className={FEEDBACK_STYLE[f.type]}>
                {f.text}
              </li>
            ))}
          </ul>
          <button onClick={onDismiss} className="mt-2 text-slate-400 hover:text-slate-600">
            Dismiss
          </button>
        </div>
      )}
    </section>
  );
}