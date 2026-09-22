"""Deterministic local tools the agent can run without a language model.

Slash commands call these directly (/jwt, /sod). A JWT pasted into a normal question is also
decoded automatically and handed to the model as extra context.
"""
from __future__ import annotations

import base64
import json
import re
from datetime import datetime, timezone

JWT_RE = re.compile(r"eyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]*")

HELP_TEXT = """**Commands**

| Command | What it does |
|---|---|
| `/jwt <token>` | Decodes a JWT locally and flags risky claims and headers. It does not verify the signature. |
| `/sod <entitlement, entitlement, ...>` | Checks a list of entitlements against common segregation-of-duties conflicts. |
| `/help` | Shows this list. |

Anything else is treated as a question and answered from the local knowledge base and the local model.

Example: `/sod Create Vendor, Approve Payment, Read Reports`"""


# ---------------------------------------------------------------- JWT

def find_jwt(text: str) -> str | None:
    match = JWT_RE.search(text)
    return match.group(0) if match else None


def _b64url_json(part: str) -> dict:
    padded = part + "=" * (-len(part) % 4)
    return json.loads(base64.urlsafe_b64decode(padded.encode()).decode("utf-8"))


def _fmt_ts(value) -> str:
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (TypeError, ValueError, OverflowError, OSError):
        return f"{value!r} (not a valid timestamp)"


def decode_jwt(token: str, now: float | None = None) -> str:
    """Decode a JWT (no signature verification) and return a markdown report."""
    token = token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    parts = token.split(".")
    if len(parts) != 3:
        return "That does not look like a JWT. A JWT has three dot-separated parts: header.payload.signature."
    try:
        header, payload = _b64url_json(parts[0]), _b64url_json(parts[1])
    except (ValueError, UnicodeDecodeError):
        return "I could not decode that token. The header or payload is not valid base64url-encoded JSON."

    now = now if now is not None else datetime.now(tz=timezone.utc).timestamp()
    findings: list[str] = []
    alg = str(header.get("alg", "")).lower()
    if alg in ("", "none"):
        findings.append("**Critical:** `alg` is missing or `none`. The token is unsigned, and a server that accepts it can be forged against.")
    elif alg.startswith("hs"):
        findings.append("Signed with a shared secret (`" + header["alg"] + "`). Anyone who can verify it can also mint tokens, so it suits single-party setups better than multi-party ones.")
    if "jku" in header or "x5u" in header or "jwk" in header:
        findings.append("**Warning:** the header carries a key-location claim (`jku`, `x5u` or `jwk`). Servers must never trust keys supplied by the token itself.")
    if "exp" not in payload:
        findings.append("**Warning:** no `exp` claim, so the token never expires.")
    else:
        try:
            exp = float(payload["exp"])
            findings.append("**Expired** at " + _fmt_ts(exp) + "." if exp < now else "Expires " + _fmt_ts(exp) + ".")
            if "iat" in payload and exp - float(payload["iat"]) > 86400:
                findings.append("Lifetime is longer than 24 hours, which is long for an access token. Prefer short-lived access tokens with refresh tokens.")
        except (TypeError, ValueError):
            findings.append("`exp` or `iat` is not a number.")
    if "nbf" in payload:
        try:
            if float(payload["nbf"]) > now:
                findings.append("`nbf` is in the future, so the token is not valid yet.")
        except (TypeError, ValueError):
            findings.append("`nbf` is not a number.")
    for claim in ("iss", "aud", "sub"):
        if claim not in payload:
            findings.append(f"No `{claim}` claim. Validators normally check issuer and audience.")
    if not parts[2]:
        findings.append("**Critical:** the signature part is empty.")

    times = {k: _fmt_ts(payload[k]) for k in ("iat", "nbf", "exp") if k in payload}
    time_lines = "\n".join(f"- `{k}`: {v}" for k, v in times.items())
    return (
        "**Header**\n```json\n" + json.dumps(header, indent=2) + "\n```\n\n"
        "**Payload**\n```json\n" + json.dumps(payload, indent=2) + "\n```\n\n"
        + ("**Timestamps**\n" + time_lines + "\n\n" if time_lines else "")
        + "**Findings**\n" + "\n".join(f"- {f}" for f in findings) + "\n\n"
        "Decoding is not validation. The signature was not checked, so never treat these claims as trusted."
    )


# ---------------------------------------------------------------- SoD

# (side A keywords, side B keywords, severity, why it matters, typical mitigation)
SOD_RULES = [
    (("create vendor", "maintain vendor", "vendor master"), ("approve payment", "release payment", "payment approval"),
     "High", "One person can create a fake vendor and pay it.", "Separate vendor maintenance from payment; add dual approval."),
    (("initiate payment", "create payment", "enter invoice"), ("approve payment", "release payment", "payment approval"),
     "High", "The same person can raise and approve a payment.", "Enforce maker-checker with different people."),
    (("create purchase order", "raise purchase order", "create po"), ("approve purchase order", "approve po", "po approval"),
     "High", "A user can self-approve their own purchasing.", "Approval limits and a different approver."),
    (("create journal", "post journal", "journal entry"), ("approve journal", "journal approval"),
     "High", "Financial records can be altered and approved by one person, a core SOX concern.", "Independent approver and periodic review."),
    (("user administration", "create user", "user admin"), ("approve access", "access approver", "access approval"),
     "High", "A user can grant access and also approve it.", "Route approvals to the resource owner or manager."),
    (("payroll maintain", "payroll master", "maintain payroll"), ("payroll approve", "process payroll", "approve payroll"),
     "High", "Payroll data can be changed and paid out by one person.", "Split maintenance from processing; reconcile payroll runs."),
    (("database admin", "dba", "system admin", "sysadmin", "domain admin"), ("audit log admin", "delete audit log", "audit configuration", "log admin"),
     "High", "An administrator could hide their own activity.", "Ship logs to a separate, write-once store owned by security."),
    (("security admin", "administrator", "admin"), ("auditor", "internal audit"),
     "High", "Auditors must be independent from the systems they audit.", "Give auditors read-only access and no admin rights."),
    (("developer", "code commit", "write code"), ("production deploy", "prod deploy", "release to production", "prod admin"),
     "Medium", "Code can go to production without independent review.", "Use CI/CD approvals and a separate release role."),
    (("create change request", "raise change"), ("approve change", "change approval"),
     "Medium", "Changes can be raised and approved by the same person.", "Change advisory board or peer approval."),
]


def _norm(text: str) -> str:
    return re.sub(r"[\s_\-:/]+", " ", text.lower()).strip()


def sod_check(raw: str) -> str:
    entitlements = [e.strip() for e in re.split(r"[,;\n]+", raw) if e.strip()]
    if len(entitlements) < 1:
        return "Give me a list of entitlements, for example: `/sod Create Vendor, Approve Payment, Read Reports`."
    normed = [(e, _norm(e)) for e in entitlements]
    rows = []
    for side_a, side_b, severity, why, fix in SOD_RULES:
        a = [e for e, n in normed if any(k in n for k in side_a)]
        b = [e for e, n in normed if any(k in n for k in side_b)]
        if a and b:
            rows.append((severity, ", ".join(dict.fromkeys(a)), ", ".join(dict.fromkeys(b)), why, fix))
    if not rows:
        return (
            f"No conflicts found among the {len(entitlements)} entitlement(s) you listed, using the built-in rule set.\n\n"
            "This is a keyword check against common conflicts. Your organisation's own SoD matrix is the authority, "
            "so confirm against it (for example the policies defined in your IGA tool)."
        )
    order = {"High": 0, "Medium": 1}
    rows.sort(key=lambda r: order.get(r[0], 2))
    table = "| Severity | Side A | Side B | Why it matters | Typical mitigation |\n|---|---|---|---|---|\n"
    table += "\n".join("| " + " | ".join(r) + " |" for r in rows)
    return (
        f"Found **{len(rows)}** potential conflict(s) among {len(entitlements)} entitlement(s).\n\n{table}\n\n"
        "If the business truly needs the combination, document a compensating control (extra approval, "
        "activity monitoring or periodic review) and have the risk owner sign it off."
    )


# ---------------------------------------------------------------- dispatcher

def run_command(message: str) -> str | None:
    """Return markdown for a slash command, or None if the message is not a command."""
    text = message.strip()
    if not text.startswith("/"):
        return None
    parts = re.split(r"\s+", text[1:], maxsplit=1)
    cmd, arg = parts[0].lower(), (parts[1] if len(parts) > 1 else "")
    if cmd == "help":
        return HELP_TEXT
    if cmd == "jwt":
        return decode_jwt(arg) if arg.strip() else "Paste a token after the command: `/jwt eyJhbGciOi...`"
    if cmd == "sod":
        return sod_check(arg)
    return f"I don't know the command `/{cmd}`. Type `/help` to see what is available."
