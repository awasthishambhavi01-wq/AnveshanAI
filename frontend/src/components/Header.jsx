const STATUS = {
  online: { dot: "bg-emerald-500", label: "Backend online" },
  offline: { dot: "bg-red-500", label: "Backend offline" },
  checking: { dot: "bg-slate-300", label: "Checking..." },
};

export default function Header({ tab, onTab, health, onToggleSidebar }) {
  const status = STATUS[health] || STATUS.checking;

  return (
    <header className="flex items-center justify-between gap-3 border-b border-slate-200 bg-white px-4 py-3">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="rounded-md border border-slate-200 px-2.5 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 md:hidden"
        >
          Documents
        </button>
        <h1 className="text-lg font-semibold tracking-tight text-indigo-600">AnveshanAI</h1>
      </div>

      <nav className="flex rounded-lg bg-slate-100 p-1 text-sm font-medium">
        {[
          ["chat", "Chat"],
          ["search", "Search"],
        ].map(([key, label]) => (
          <button
            key={key}
            onClick={() => onTab(key)}
            className={`rounded-md px-4 py-1.5 transition ${
              tab === key ? "bg-white text-indigo-600 shadow-sm" : "text-slate-500 hover:text-slate-700"
            }`}
          >
            {label}
          </button>
        ))}
      </nav>

      <div className="hidden items-center gap-2 text-xs text-slate-500 sm:flex">
        <span className={`h-2 w-2 rounded-full ${status.dot}`} />
        {status.label}
      </div>
    </header>
  );
}