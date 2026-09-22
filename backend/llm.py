"""Thin client for a local Ollama server (https://ollama.com)."""
from __future__ import annotations

import json
from typing import Iterator

import requests

from backend import config


class LLMUnavailable(Exception):
    """Raised when the local model cannot be reached or is not installed."""


def status() -> dict:
    """Quick health probe used by the UI status indicator."""
    model = config.OLLAMA_MODEL
    try:
        resp = requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=1.5)
        resp.raise_for_status()
        names = [m.get("name", "") for m in resp.json().get("models", [])]
    except (requests.RequestException, ValueError):
        return {"online": False, "model": model, "installed": False, "models": []}
    installed = any(n == model or n == f"{model}:latest" or n.startswith(f"{model}:") for n in names)
    return {"online": True, "model": model, "installed": installed, "models": names}


def stream_chat(messages: list[dict], model: str | None = None) -> Iterator[str]:
    """Open a streaming chat request. Connection problems raise LLMUnavailable immediately;
    the returned iterator yields text fragments as the model produces them."""
    model = model or config.OLLAMA_MODEL
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {"temperature": 0.2, "num_ctx": config.NUM_CTX},
    }
    try:
        resp = requests.post(
            f"{config.OLLAMA_URL}/api/chat",
            json=payload,
            stream=True,
            timeout=(3, config.LLM_TIMEOUT),
        )
    except requests.RequestException as exc:
        raise LLMUnavailable(f"Cannot reach Ollama at {config.OLLAMA_URL}") from exc

    if resp.status_code == 404:
        resp.close()
        raise LLMUnavailable(f"Model '{model}' is not installed. Run: ollama pull {model}")
    if resp.status_code != 200:
        resp.close()
        raise LLMUnavailable(f"Ollama returned HTTP {resp.status_code}")

    def fragments() -> Iterator[str]:
        with resp:
            for line in resp.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                if "error" in data:
                    raise LLMUnavailable(str(data["error"]))
                token = data.get("message", {}).get("content", "")
                if token:
                    yield token
                if data.get("done"):
                    break

    return fragments()
