"""A small BM25 retriever over the markdown files in /knowledge.

Pure Python: no vector database, no embeddings model, no downloads. Each `##` section of a
markdown file becomes one searchable chunk. Drop new .md files into /knowledge and restart
(or call POST /api/reload) to teach the agent more.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

STOPWORDS = frozenset(
    """a an the and or but if then else of to in on at by for with from as is are was were be been
    being do does did done how what why when where which who whom whose this that these those it its
    can could should would will shall may might must i you we they he she me my your our their about
    into over under between vs versus difference explain tell give show please""".split()
)

# Short forms people type, expanded so they match the long form used in the notes.
ALIASES = {
    "jml": "joiner mover leaver",
    "sod": "segregation duties",
    "iga": "identity governance administration",
    "pam": "privileged access management",
    "mfa": "multi factor authentication",
    "2fa": "multi factor authentication",
    "sso": "single sign",
    "iiq": "identityiq",
    "isc": "identity security cloud",
    "rbac": "role based access control",
    "abac": "attribute based access control",
    "idp": "identity provider",
    "oidc": "openid connect",
    "itdr": "identity threat detection response",
    "ciam": "customer identity",
    "uat": "user acceptance testing",
    "cpm": "central policy manager",
    "psm": "privileged session manager",
    "pvwa": "password vault web access",
    "lcm": "lifecycle manager",
    "zt": "zero trust",
    "zsp": "zero standing privilege",
    "xss": "cross site scripting",
    "csrf": "cross site request forgery",
    "sqli": "sql injection",
    "ssrf": "server side request forgery",
    "idor": "insecure direct object reference broken access control",
    "sast": "static application security testing",
    "dast": "dynamic application security testing",
    "sca": "software composition analysis",
    "ztna": "zero trust network access",
    "nac": "network access control",
    "ngfw": "next generation firewall",
    "ids": "intrusion detection system",
    "ips": "intrusion prevention system",
    "ir": "incident response",
    "siem": "security information event management",
    "cve": "vulnerability",
    "owasp": "open web application security project",
    "pentest": "penetration testing",
    "vapt": "vulnerability assessment penetration testing",
}

_TOKEN = re.compile(r"[a-z0-9]+")


def _stem(tok: str) -> str:
    """Very light stemming so 'roles', 'provisioning' and 'provisioned' meet in the middle."""
    if len(tok) <= 4:
        return tok
    if tok.endswith("ies"):
        return tok[:-3] + "y"
    for suffix in ("ing", "ed", "es", "ly"):
        if tok.endswith(suffix) and len(tok) - len(suffix) >= 4:
            return tok[: -len(suffix)]
    if tok.endswith("s") and not tok.endswith("ss"):
        return tok[:-1]
    return tok


def _normalise(text: str) -> str:
    text = text.lower()
    text = re.sub(r"oauth\s*2(\.0)?", "oauth", text)
    text = re.sub(r"saml\s*2(\.0)?", "saml", text)
    return text


def tokenize(text: str, expand: bool = False) -> list[str]:
    out: list[str] = []
    for tok in _TOKEN.findall(_normalise(text)):
        if expand and tok in ALIASES:
            out.extend(_stem(w) for w in ALIASES[tok].split() if w not in STOPWORDS)
        if tok in STOPWORDS:
            continue
        out.append(_stem(tok))
    return out


@dataclass
class Chunk:
    id: int
    doc: str
    title: str
    heading: str
    text: str
    tokens: list[str] = field(default_factory=list, repr=False)


@dataclass
class Hit:
    chunk: Chunk
    score: float
    relevance: float  # 0..1, relative to the best hit for this query


MAX_CHUNK_CHARS = 1400
TARGET_CHUNK_CHARS = 1100


def _split_long(text: str) -> list[str]:
    if len(text) <= MAX_CHUNK_CHARS:
        return [text]
    pieces, current = [], ""
    for para in text.split("\n\n"):
        if current and len(current) + len(para) > TARGET_CHUNK_CHARS:
            pieces.append(current.strip())
            current = ""
        current += para + "\n\n"
    if current.strip():
        pieces.append(current.strip())
    return pieces


def load_chunks(knowledge_dir: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(knowledge_dir.glob("*.md")):
        title = path.stem.replace("_", " ").title()
        heading, buf, sections = "Overview", [], []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
            elif line.startswith("## "):
                sections.append((heading, "\n".join(buf)))
                heading, buf = line[3:].strip(), []
            else:
                buf.append(line)
        sections.append((heading, "\n".join(buf)))
        for head, body in sections:
            body = body.strip()
            if not body:
                continue
            for piece in _split_long(body):
                chunks.append(Chunk(len(chunks), path.stem, title, head, piece))
    return chunks


class Retriever:
    K1 = 1.5
    B = 0.75

    def __init__(self, knowledge_dir: Path):
        self.knowledge_dir = Path(knowledge_dir)
        self.chunks: list[Chunk] = []
        self.reload()

    def reload(self) -> None:
        self.chunks = load_chunks(self.knowledge_dir)
        self._tf: list[Counter] = []
        self._len: list[int] = []
        self._df: Counter = Counter()
        for c in self.chunks:
            # Headings are weighted double: they are the best summary of a chunk.
            c.tokens = tokenize(c.heading) * 2 + tokenize(c.title) + tokenize(c.text)
            tf = Counter(c.tokens)
            self._tf.append(tf)
            self._len.append(len(c.tokens))
            self._df.update(tf.keys())
        self._avgdl = (sum(self._len) / len(self._len)) if self._len else 1.0

    def stats(self) -> dict:
        return {"documents": len({c.doc for c in self.chunks}), "chunks": len(self.chunks)}

    def search(self, query: str, k: int = 4, min_relevance: float = 0.35) -> list[Hit]:
        terms = set(tokenize(query, expand=True))
        if not terms or not self.chunks:
            return []
        n = len(self.chunks)
        scored: list[tuple[float, int]] = []
        for i, tf in enumerate(self._tf):
            score = 0.0
            for term in terms:
                freq = tf.get(term)
                if not freq:
                    continue
                df = self._df[term]
                idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
                norm = freq + self.K1 * (1 - self.B + self.B * self._len[i] / self._avgdl)
                score += idf * freq * (self.K1 + 1) / norm
            if score > 0:
                scored.append((score, i))
        if not scored:
            return []
        scored.sort(reverse=True)
        best = scored[0][0]
        hits = [Hit(self.chunks[i], s, s / best) for s, i in scored[:k]]
        return [h for h in hits if h.relevance >= min_relevance]
