import { useState } from "react";
import SourceCard from "./SourceCard";

// Turn [1], [2] in the answer into clickable markers. Markers with no matching
// source (small models sometimes invent them) stay as plain text.
function AnswerText({ text, sources, onCite }) {
  const valid = new Set(sources.map((s) => s.id));
  const parts = text.split(/(\[\d+\])/g);

  return (
    <p className="whitespace-pre-wrap leading-relaxed">
      {parts.map((part, i) => {
        const match = part.match(/^\[(\d+)\]$/);
        if (match && valid.has(Number(match[1]))) {
          return (
            <button
              key={i}
              onClick={() => onCite(Number(match[1]))}
              className="mx-0.5 inline-flex h-5 min-w-5 items-center justify-center rounded bg-indigo-100 px-1 align-text-top text-xs font-semibold text-indigo-700 hover:bg-indigo-200"
            >
              {match[1]}
            </button>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </p>
  );
}

export default function MessageBubble({ message }) {
  const [showSources, setShowSources] = useState(false);
  const [activeSource, setActiveSource] = useState(null);

  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] whitespace-pre-wrap rounded-2xl rounded-br-sm bg-indigo-600 px-4 py-2.5 text-white">
          {message.content}
        </div>
      </div>
    );
  }

  const sources = message.sources || [];

  return (
    <div className="flex justify-start">
      <div className="max-w-[90%] rounded-2xl rounded-bl-sm border border-slate-200 bg-white px-4 py-3 text-slate-800 shadow-sm">
        <AnswerText
          text={message.content}
          sources={sources}
          onCite={(id) => {
            setShowSources(true);
            setActiveSource(id);
          }}
        />

        {message.rewritten && (
          <p className="mt-2 text-xs italic text-slate-400">Searched for: {message.rewritten}</p>
        )}

        {sources.length > 0 && (
          <div className="mt-3">
            <button
              onClick={() => setShowSources((v) => !v)}
              className="text-xs font-medium text-indigo-600 hover:underline"
            >
              {showSources ? "Hide" : "Show"} sources ({sources.length})
            </button>
            {showSources && (
              <div className="mt-2 space-y-2">
                {sources.map((s) => (
                  <SourceCard key={s.id} source={s} highlighted={activeSource === s.id} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}