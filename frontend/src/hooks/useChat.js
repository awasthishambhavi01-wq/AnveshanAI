import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";

const SESSION_KEY = "anveshanai_session_id";

const uid = () => Math.random().toString(36).slice(2);

const readStored = () => {
  try {
    return localStorage.getItem(SESSION_KEY);
  } catch {
    return null;
  }
};
const writeStored = (id) => {
  try {
    if (id) localStorage.setItem(SESSION_KEY, id);
    else localStorage.removeItem(SESSION_KEY);
  } catch {
    /* storage unavailable: chat still works, it just won't survive a refresh */
  }
};

export function useChat(selectedIds) {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sending, setSending] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [error, setError] = useState(null);

  // Restore the previous conversation after a refresh
  useEffect(() => {
    const stored = readStored();
    if (!stored) {
      setInitializing(false);
      return;
    }
    let cancelled = false;
    api
      .getMessages(stored)
      .then((rows) => {
        if (cancelled) return;
        setSessionId(stored);
        setMessages(
          rows.map((m) => ({
            id: uid(),
            role: m.role,
            content: m.content,
            sources: m.sources || [],
          }))
        );
      })
      .catch((e) => {
        if (e.status === 404) writeStored(null); // session no longer exists
        else if (!cancelled) setError(e.message);
      })
      .finally(() => {
        if (!cancelled) setInitializing(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const newChat = useCallback(() => {
    writeStored(null);
    setSessionId(null);
    setMessages([]);
    setError(null);
  }, []);

  // Returns true on success so the input box knows whether to keep the text
  const send = useCallback(
    async (question) => {
      const text = question.trim();
      if (!text || sending) return false;

      setError(null);
      setSending(true);
      const userMsg = { id: uid(), role: "user", content: text };
      setMessages((prev) => [...prev, userMsg]);

      try {
        let sid = sessionId;
        if (!sid) {
          // Created lazily so empty sessions never pile up in the database
          const created = await api.createSession();
          sid = created.session_id;
          setSessionId(sid);
          writeStored(sid);
        }

        const res = await api.chat({ question: text, sessionId: sid, docIds: selectedIds });

        setMessages((prev) => [
          ...prev,
          {
            id: uid(),
            role: "assistant",
            content: res.answer,
            sources: res.sources || [],
            rewritten:
              res.rewritten_question && res.rewritten_question !== text
                ? res.rewritten_question
                : null,
          },
        ]);
        return true;
      } catch (e) {
        // The backend does not save a failed exchange, so remove it here too
        setMessages((prev) => prev.filter((m) => m.id !== userMsg.id));
        if (e.status === 404 && sessionId) {
          writeStored(null);
          setSessionId(null);
          setError("That conversation no longer exists. Please send your question again.");
        } else {
          setError(e.message);
        }
        return false;
      } finally {
        setSending(false);
      }
    },
    [sessionId, sending, selectedIds]
  );

  return {
    messages,
    sending,
    initializing,
    error,
    send,
    newChat,
    dismissError: () => setError(null),
  };
}