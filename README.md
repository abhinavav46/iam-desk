# IAM Desk

*Built by Abhinav A V*

A local AI agent for the identity and access management (IAM) and cybersecurity domain — SAML/OIDC/OAuth, SailPoint IGA, PAM, network & application security, incident response, security testing, identity attacks, and compliance. HTML/CSS/JS front end, Python (Flask) backend, and a locally-run language model. Nothing leaves your machine.

```
┌─────────────┐   fetch (NDJSON stream)   ┌──────────────┐   local HTTP   ┌──────────┐
│  Browser UI │ ────────────────────────▶ │ Flask backend │ ─────────────▶ │  Ollama  │
│ (frontend/) │ ◀──────────────────────── │ (backend/)    │ ◀───────────── │ (model)  │
└─────────────┘                           └───────┬──────┘                └──────────┘
                                                   │
                                          BM25 search over
                                          knowledge/*.md
```

## What it does

- Chat UI in the browser, styled like a small security console (`frontend/`).
- A Flask backend (`backend/app.py`) that streams responses token-by-token over NDJSON.
- Retrieval over a local knowledge base of Markdown notes (`knowledge/`) covering IAM fundamentals, authentication/MFA, authorization models, SAML/OAuth/OIDC/SCIM, SailPoint IGA, PAM, identity attacks & detection, compliance/cloud IAM, network & application security (OWASP-style categories), incident response, and IAM-focused security/QA testing — using a small BM25 implementation with **no external dependencies or embedding downloads** (`backend/retriever.py`).
- A locally-run language model, via [Ollama](https://ollama.com), so nothing is sent to any cloud API. If Ollama isn't running, the app still answers by showing the most relevant notes directly (`backend/agent.py`).
- Two built-in offline tools that don't need the model at all (`backend/tools.py`):
  - `/jwt <token>` — decodes a JWT locally and flags risky claims (`alg: none`, missing `exp`, missing `aud`/`iss`, etc.). It only decodes; it never verifies a signature.
  - `/sod <entitlement, entitlement, ...>` — checks a list of entitlements against common segregation-of-duties conflicts (e.g. "Create Vendor" + "Approve Payment").
- A small unit test suite (`tests/`) covering the retriever and both tools, runnable with no model installed.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running, with a model pulled (a small general-purpose model like `llama3.2` or `qwen2.5:7b` works well). The chat UI still works without it — see "Running without a model" below.

## Quick start

1. **Install Ollama and pull a model** (skip this if you'd rather test the app without a model first):
   ```bash
   ollama pull llama3.2
   ollama serve      # if it isn't already running as a background service
   ```
2. **Clone and run:**
   ```bash
   git clone <your-fork-url> iam-desk
   cd iam-desk
   ./run.sh           # macOS / Linux
   run.bat             # Windows
   ```
   This creates a virtual environment, installs `requirements.txt`, and starts the server.
3. Open **http://127.0.0.1:5000** in your browser.

If you'd rather do it by hand:
```bash
python3 -m venv .venv
source .venv/bin/activate      # .venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m backend.app
```

## Configuration

Copy `.env.example` to `.env` and adjust as needed — every setting has a sane default in `backend/config.py`:

| Variable | Default | Meaning |
|---|---|---|
| `OLLAMA_URL` | `http://localhost:11434` | Where the local model server is listening |
| `OLLAMA_MODEL` | `llama3.2` | Model name (must be pulled with `ollama pull`) |
| `HOST` / `PORT` | `127.0.0.1` / `5000` | Where the Flask app listens |
| `TOP_K` | `4` | How many knowledge-base sections to retrieve per question |
| `MAX_HISTORY` | `8` | How many past turns are sent back to the model |

## Running without a model

If Ollama isn't installed or running, the sidebar status dot turns red and the agent automatically falls back to showing the most relevant notes from `knowledge/` directly, so the app is still useful and testable on a machine with no model set up. `/jwt` and `/sod` work either way, since they don't call the model.

## Extending the knowledge base

Drop a new `.md` file into `knowledge/`. Use `##` headings — each one becomes a separately searchable chunk. Restart the server, or `POST /api/reload`, to pick it up:
```bash
curl -X POST http://127.0.0.1:5000/api/reload
```

## Project layout

```
iam-desk/
├── backend/
│   ├── app.py          Flask app: routes, health check, NDJSON chat stream
│   ├── agent.py         Ties retrieval + tools + the local model together
│   ├── retriever.py     Dependency-free BM25 search over knowledge/*.md
│   ├── llm.py            Streaming client for a local Ollama server
│   ├── tools.py          /jwt and /sod offline tools
│   └── config.py         All settings, with .env support
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js            No build step — plain JS, fetch + streaming reader
├── knowledge/             Markdown notes the agent retrieves from
├── tests/                 Unit tests (no model required)
├── run.sh / run.bat
├── requirements.txt
└── .env.example
```

## Running the tests

```bash
python -m unittest discover -s tests -v
```
A GitHub Actions workflow (`.github/workflows/tests.yml`) runs the same suite on every push.

## Publishing to GitHub

```bash
cd iam-desk
git init
git add .
git commit -m "Initial commit: IAM Desk local AI agent"
git branch -M main
git remote add origin https://github.com/<your-username>/iam-desk.git
git push -u origin main
```
`.env` and `.venv/` are already excluded via `.gitignore`, so no local secrets or environments get committed.

## Notes and limitations

- This is a study and demo tool, not a security product. `/jwt` decodes tokens for learning purposes only — it never verifies a signature, and none of its output should be used as the basis for a real access decision.
- `/sod` uses a small built-in keyword rule set to illustrate common conflicts; it isn't a substitute for your organisation's actual SoD policy matrix (e.g. the one configured in SailPoint or Saviynt).
- The knowledge base is a fixed set of notes, not a live feed — accurate as of when it was written, not a substitute for current vendor documentation.
