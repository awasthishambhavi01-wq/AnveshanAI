import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";

export function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]); // empty = use all ready documents
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [feedback, setFeedback] = useState([]); // [{type, text}]

  const refresh = useCallback(async () => {
    try {
      const docs = await api.listDocuments();
      setDocuments(docs);
      // drop selections for documents that no longer exist or are not ready
      setSelectedIds((prev) =>
        prev.filter((id) => docs.some((d) => d.id === id && d.status === "ready"))
      );
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // Upload is synchronous on the backend: when the request returns, status is ready or failed
  const upload = useCallback(
    async (files) => {
      setUploading(true);
      const results = [];
      for (const file of files) {
        try {
          const res = await api.uploadDocument(file);
          if (res.duplicate) {
            results.push({ type: "info", text: `${file.name} was already uploaded.` });
          } else if (res.status === "failed") {
            results.push({ type: "error", text: `${file.name} could not be processed.` });
          } else {
            results.push({ type: "success", text: `${file.name} is ready.` });
          }
        } catch (e) {
          results.push({ type: "error", text: `${file.name}: ${e.message}` });
        }
      }
      setFeedback(results);
      await refresh();
      setUploading(false);
    },
    [refresh]
  );

  const remove = useCallback(
    async (id) => {
      try {
        await api.deleteDocument(id);
        setSelectedIds((prev) => prev.filter((x) => x !== id));
        await refresh();
      } catch (e) {
        setError(e.message);
      }
    },
    [refresh]
  );

  const toggle = useCallback((id) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }, []);

  return {
    documents,
    selectedIds,
    loading,
    uploading,
    error,
    feedback,
    upload,
    remove,
    refresh,
    toggle,
    clearSelection: () => setSelectedIds([]),
    dismissFeedback: () => setFeedback([]),
  };
}