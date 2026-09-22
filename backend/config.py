"""Central configuration. Every value can be overridden with an environment variable
or a `.env` file in the project root (see `.env.example`)."""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader so the project needs no extra dependency."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv(BASE_DIR / ".env")

KNOWLEDGE_DIR = BASE_DIR / "knowledge"
FRONTEND_DIR = BASE_DIR / "frontend"

# Local LLM served by Ollama (https://ollama.com). Nothing leaves your machine.
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
NUM_CTX = int(os.getenv("NUM_CTX", "4096"))
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "180"))  # seconds to wait for the next token

# Web server. 127.0.0.1 keeps the app reachable from this machine only.
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))

# Retrieval and conversation limits.
TOP_K = int(os.getenv("TOP_K", "4"))
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "8"))
MAX_MESSAGE_CHARS = int(os.getenv("MAX_MESSAGE_CHARS", "4000"))
