import { useState } from "react";

export default function ChatInput({ onSend, disabled, placeholder }) {
  const [value, setValue] = useState("");

  const submit = async () => {
    const text = value.trim();
    if (!text || disabled) return;
    setValue("");
    const ok = await onSend(text);
    if (!ok) setValue(text); // restore the question if the request failed
  };

  return (
    <div className="flex items-end gap-2 border-t border-slate-200 bg-white p-3">
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submit();
          }
        }}
        rows={1}
        disabled={disabled}
        placeholder={placeholder}
        className="max-h-40 min-h-11 flex-1 resize-none rounded-xl border border-slate-300 px-4 py-2.5 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 disabled:bg-slate-100"
      />
      <button
        onClick={submit}
        disabled={disabled || !value.trim()}
        className="h-11 rounded-xl bg-indigo-600 px-5 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        Send
      </button>
    </div>
  );
}