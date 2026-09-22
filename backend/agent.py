"""The agent: routes a message to a tool or to retrieval + local LLM, and streams events."""
from __future__ import annotations

from typing import Iterator

import requests

from backend import config, llm, tools
from backend.retriever import Hit, Retriever

SYSTEM_PROMPT = """You are IAM Desk, a careful assistant for identity and access management (IAM) and cybersecurity more broadly.
You help IAM engineers, testers, analysts and security-adjacent developers with:
- Authentication, authorization, federation (SAML, OAuth 2.0, OIDC), identity governance (IGA), privileged access
  management (PAM), SailPoint, cloud IAM, zero trust and identity-based attacks.
- Wider cybersecurity topics: network security (firewalls, segmentation, ZTNA, IDS/IPS), application security
  (the OWASP-style categories: injection, broken access control, XSS, CSRF, SSRF, misconfig, vulnerable components),
  security testing (SAST, DAST, SCA, pentesting, vulnerability scanning), and incident response (detection,
  containment, eradication, recovery, identity-specific IR such as revoking sessions and compromised-account handling).
- QA/testing angles on IAM features (access requests, certifications, provisioning, SoD checks), since many users
  of this tool also do functional/UAT testing.

How to answer:
- Use the CONTEXT excerpts when they are relevant. If the context does not cover the question, say so briefly, then answer
  from general knowledge and make clear which part is general knowledge.
- Be concise and structured: a short direct answer first, then details, steps or a small table if it helps.
- Never invent product menu paths, API names, CLI flags, configuration keys or version numbers. When a detail depends on the
  product version, say so and suggest checking the vendor documentation.
- Prefer defensive guidance. Explain how attacks work at a conceptual level and focus on detection and prevention.
- Do not ask for or repeat real passwords, secrets or private keys. If the user pastes one, tell them to rotate it.
- If the question is unrelated to IAM or cybersecurity, say this assistant is focused on that domain and steer back."""

MAX_CONTEXT_CHARS = 5500


def _clean_history(history) -> list[dict]:
    """Keep only well-formed user/assistant turns, trimmed to the configured window."""
    cleaned = []
    for item in history or []:
        if not isinstance(item, dict):
            continue
        role, content = item.get("role"), item.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            cleaned.append({"role": role, "content": content[:2000]})
    return cleaned[-config.MAX_HISTORY :]


def _build_context(hits: list[Hit]) -> str:
    blocks, used = [], 0
    for i, hit in enumerate(hits, 1):
        block = f"[{i}] {hit.chunk.title} - {hit.chunk.heading}\n{hit.chunk.text}"
        if used + len(block) > MAX_CONTEXT_CHARS and blocks:
            break
        blocks.append(block)
        used += len(block)
    return "\n\n".join(blocks)


def _kb_answer(hits: list[Hit], reason: str) -> str:
    """Fallback used when the local model is not running: show the best notes directly."""
    if not hits:
        return (
            "I could not find anything about that in the local knowledge base, and the local model is not running "
            "to answer from general knowledge.\n\n" + reason
        )
    parts = ["**The local model is offline, so this is a direct look-up from the knowledge base.**"]
    for hit in hits[:2]:
        parts.append(f"#### {hit.chunk.heading}\n*{hit.chunk.title}*\n\n{hit.chunk.text}")
    parts.append(reason)
    return "\n\n".join(parts)


class Agent:
    def __init__(self) -> None:
        self.retriever = Retriever(config.KNOWLEDGE_DIR)

    def _retrieval_query(self, message: str, history: list[dict]) -> str:
        # Short follow-ups ("and for cloud?") borrow the previous question for context.
        if len(message.split()) < 6:
            previous = [h["content"] for h in history if h["role"] == "user"]
            if previous:
                return previous[-1] + " " + message
        return message

    def respond(self, message: str, history=None) -> Iterator[dict]:
        history = _clean_history(history)

        # 1. Slash commands are handled locally without the model.
        command_output = tools.run_command(message)
        if command_output is not None:
            yield {"type": "meta", "mode": "tool", "sources": []}
            yield {"type": "token", "text": command_output}
            yield {"type": "done"}
            return

        # 2. Retrieve relevant notes from the local knowledge base.
        hits = self.retriever.search(self._retrieval_query(message, history), k=config.TOP_K)
        sources = [
            {"title": h.chunk.title, "heading": h.chunk.heading, "doc": h.chunk.doc, "relevance": round(h.relevance, 2)}
            for h in hits
        ]

        # 3. If the message contains a JWT, decode it locally and give the result to the model.
        extra = ""
        token = tools.find_jwt(message)
        if token:
            extra = "TOOL RESULT (local JWT decoder):\n" + tools.decode_jwt(token) + "\n\n"

        context = _build_context(hits) or "(no relevant notes were found for this question)"
        user_turn = f"CONTEXT:\n{context}\n\n{extra}QUESTION:\n{message}"
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, *history, {"role": "user", "content": user_turn}]

        # 4. Ask the local model. If it is unavailable, fall back to the knowledge base.
        try:
            stream = llm.stream_chat(messages)
        except llm.LLMUnavailable as exc:
            reason = f"*{exc}.* See the README to start Ollama and pull a model."
            yield {"type": "meta", "mode": "kb", "sources": sources, "reason": str(exc)}
            yield {"type": "token", "text": _kb_answer(hits, reason)}
            yield {"type": "done"}
            return

        yield {"type": "meta", "mode": "llm", "model": config.OLLAMA_MODEL, "sources": sources}
        try:
            for fragment in stream:
                yield {"type": "token", "text": fragment}
        except (llm.LLMUnavailable, requests.RequestException) as exc:
            yield {"type": "error", "message": f"The local model stopped responding: {exc}"}
        yield {"type": "done"}
