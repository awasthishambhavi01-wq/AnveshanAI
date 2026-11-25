const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

// FastAPI returns {detail: "text"} for 400/404/503 and {detail: [{msg}, ...]} for 422
function formatDetail(detail) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join("; ");
  return "Something went wrong.";
}

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${BASE}${path}`, options);
  } catch {
    throw new ApiError("Cannot reach the backend. Is the server running?", 0);
  }

  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body.detail) message = formatDetail(body.detail);
    } catch {
      /* response had no JSON body */
    }
    throw new ApiError(message, res.status);
  }
  return res.json();
}

const jsonBody = (method, body) => ({
  method,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export const api = {
  health: () => request("/health"),

  listDocuments: () => request("/documents"),
  uploadDocument: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/documents", { method: "POST", body: form });
  },
  deleteDocument: (id) => request(`/documents/${id}`, { method: "DELETE" }),

  // docIds empty or undefined = search all documents
  search: (query, topK = 5, docIds) =>
    request("/search", jsonBody("POST", {
      query,
      top_k: topK,
      doc_ids: docIds?.length ? docIds : null,
    })),

  createSession: () => request("/sessions", { method: "POST" }),
  getMessages: (sessionId) => request(`/sessions/${sessionId}/messages`),

  chat: ({ question, sessionId, docIds }) =>
    request("/chat", jsonBody("POST", {
      question,
      session_id: sessionId ?? null,
      doc_ids: docIds?.length ? docIds : null,
    })),
};