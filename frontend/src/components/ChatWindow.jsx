import { useEffect, useRef, useState } from "react";
import ChatInput from "./ChatInput";
import MessageBubble from "./MessageBubble";

// Local models can take over a minute, so show elapsed time instead of a bare spinner
function Thinking() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex justify-start">
      <div className="rounded-2xl rounded-bl-sm border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" />
          Searching your documents... {seconds}s
        </div>
        {seconds >= 20 && (
          <p className="mt-1 text-xs text-slate-400">
            The local model is still working. This can take a while on CPU.
          </p>
        )}
      </div>
    </div>
  );
}

export default function ChatWindow({
  messages,
  sending,
  initializing,
  error,
  onSend,
  onNewChat,
  onDismissError,
  readyCount,
  selectedCount,
}) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const noDocs = readyCount === 0;
  const scope =
    selectedCount > 0
      ? `${selectedCount} selected document${selectedCount > 1 ? "s" : ""}`
      : `all ${readyCount} ready document${readyCount === 1 ? "" : "s"}`;

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-2 text-xs text-slate-500">
        <span>{noDocs ? "No documents ready" : `Answering from ${scope}`}</span>
        <button
          onClick={onNewChat}
          disabled={sending || messages.length === 0}
          className="rounded-md border border-slate-200 px-3 py-1 font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-40"
        >
          New chat
        </button>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {initializing && <p className="text-sm text-slate-400">Loading conversation...</p>}

        {!initializing && messages.length === 0 && (
          <div className="mx-auto mt-16 max-w-md text-center">
            <h2 className="text-xl font-semibold text-slate-800">Ask your documents anything</h2>
            <p className="mt-2 text-sm text-slate-500">
              {noDocs
                ? "Upload a PDF in the sidebar first. Answers will cite the file and page they came from."
                : "Answers cite the file and page they came from, and follow-up questions remember the conversation."}
            </p>
          </div>
        )}

        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        {sending && <Thinking />}
        <div ref={bottomRef} />
      </div>

      {error && (
        <div className="flex items-start justify-between gap-3 border-t border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
          <span>{error}</span>
          <button onClick={onDismissError} className="shrink-0 text-red-400 hover:text-red-600">
            Dismiss
          </button>
        </div>
      )}

      <ChatInput
        onSend={onSend}
        disabled={sending || initializing || noDocs}
        placeholder={noDocs ? "Upload a PDF to start chatting" : "Ask a question..."}
      />
    </div>
  );
}