"""Flask app: serves the UI and exposes a small JSON/NDJSON API.

Run from the project root:   python -m backend.app
"""
from __future__ import annotations

import json

from flask import Flask, Response, jsonify, request, send_from_directory, stream_with_context

from backend import config, llm
from backend.agent import Agent

app = Flask(__name__, static_folder=str(config.FRONTEND_DIR), static_url_path="/static")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
agent = Agent()


@app.get("/")
def index():
    return send_from_directory(config.FRONTEND_DIR, "index.html")


@app.get("/api/health")
def health():
    return jsonify({"llm": llm.status(), "knowledge": agent.retriever.stats()})


@app.post("/api/reload")
def reload_knowledge():
    agent.retriever.reload()
    return jsonify(agent.retriever.stats())


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    if not message:
        return jsonify(error="The message is empty."), 400
    if len(message) > config.MAX_MESSAGE_CHARS:
        return jsonify(error=f"The message is longer than {config.MAX_MESSAGE_CHARS} characters."), 413
    history = data.get("history") or []

    def generate():
        for event in agent.respond(message, history):
            yield json.dumps(event, ensure_ascii=False) + "\n"

    return Response(
        stream_with_context(generate()),
        mimetype="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def main() -> None:
    stats = agent.retriever.stats()
    print(f"IAM Desk is running at http://{config.HOST}:{config.PORT}")
    print(f"Knowledge base: {stats['documents']} documents, {stats['chunks']} sections")
    print(f"Local model: {config.OLLAMA_MODEL} via {config.OLLAMA_URL}  (press Ctrl+C to stop)")
    app.run(host=config.HOST, port=config.PORT, debug=False, threaded=True)


if __name__ == "__main__":
    main()
