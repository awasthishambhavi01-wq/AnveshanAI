NOT_FOUND_MESSAGE = "I couldn't find this in the documents."

SYSTEM_PROMPT = f"""You are a document assistant. Answer ONLY using the numbered context passages provided.
Rules:
- If the answer is not in the context, reply exactly: "{NOT_FOUND_MESSAGE}"
- Cite the passages you used like [1], [2] right after the claim they support.
- Do not use outside knowledge. Do not invent facts.
- Keep the answer clear and concise."""


def build_messages(question: str, chunks: list[dict]) -> list[dict]:
    context = "\n\n".join(
        f"[{i}] ({c['filename']}, p.{c['page']}): {c['text']}"
        for i, c in enumerate(chunks, start=1)
    )
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]