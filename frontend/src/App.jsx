import { useState } from "react";
import ChatWindow from "./components/ChatWindow";
import DocumentList from "./components/DocumentList";
import Header from "./components/Header";
import SearchPanel from "./components/SearchPanel";
import UploadPanel from "./components/UploadPanel";
import { useChat } from "./hooks/useChat";
import { useDocuments } from "./hooks/useDocuments";
import { useHealth } from "./hooks/useHealth";

export default function App() {
  const [tab, setTab] = useState("chat");
  const [sidebarOpen, setSidebarOpen] = useState(false); // mobile only

  const docs = useDocuments();
  const chat = useChat(docs.selectedIds);
  const health = useHealth();

  const readyCount = docs.documents.filter((d) => d.status === "ready").length;

  return (
    <div className="flex h-full flex-col bg-slate-50 text-slate-900">
      <Header
        tab={tab}
        onTab={(t) => {
          setTab(t);
          setSidebarOpen(false);
        }}
        health={health}
        onToggleSidebar={() => setSidebarOpen((v) => !v)}
      />

      {health === "offline" && (
        <div className="bg-red-600 px-4 py-1.5 text-center text-sm text-white">
          Cannot reach the backend at {import.meta.env.VITE_API_URL || "http://localhost:8000"}. Start it with
          uvicorn.
        </div>
      )}

      <div className="flex min-h-0 flex-1">
        <aside
          className={`${sidebarOpen ? "flex" : "hidden"} w-full shrink-0 flex-col gap-5 overflow-y-auto border-r border-slate-200 bg-white p-4 md:flex md:w-80`}
        >
          <UploadPanel
            onUpload={docs.upload}
            uploading={docs.uploading}
            feedback={docs.feedback}
            onDismiss={docs.dismissFeedback}
          />
          <DocumentList
            documents={docs.documents}
            selectedIds={docs.selectedIds}
            loading={docs.loading}
            error={docs.error}
            onToggle={docs.toggle}
            onDelete={docs.remove}
            onClearSelection={docs.clearSelection}
            onRefresh={docs.refresh}
          />
        </aside>

        <main className={`${sidebarOpen ? "hidden" : "flex"} min-w-0 flex-1 flex-col md:flex`}>
          {tab === "chat" ? (
            <ChatWindow
              messages={chat.messages}
              sending={chat.sending}
              initializing={chat.initializing}
              error={chat.error}
              onSend={chat.send}
              onNewChat={chat.newChat}
              onDismissError={chat.dismissError}
              readyCount={readyCount}
              selectedCount={docs.selectedIds.length}
            />
          ) : (
            <SearchPanel selectedIds={docs.selectedIds} readyCount={readyCount} />
          )}
        </main>
      </div>
    </div>
  );
}