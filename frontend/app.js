"use strict";

/* IAM Desk frontend — no build step, no frameworks. Talks to /api/chat (NDJSON stream)
   and /api/health, and renders a light markdown subset locally. */

const chatScroll = document.getElementById("chatScroll");
const composer = document.getElementById("composer");
const input = document.getElementById("input");
const sendBtn = document.getElementById("sendBtn");
const llmStatusEl = document.getElementById("llmStatus");
const kbStatusEl = document.getElementById("kbStatus");

let history = [];   // [{role, content}]
let sending = false;

// ---------------------------------------------------------------- markdown (tiny, safe subset)

function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function renderInline(text) {
  let out = escapeHtml(text);
  out = out.replace(/`([^`]+)`/g, "<code>$1</code>");
  out = out.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  return out;
}

function renderMarkdown(md) {
  const lines = md.replace(/\r\n/g, "\n").split("\n");
  let html = "";
  let i = 0;
  let inList = null; // 'ul' | 'ol' | null

  function closeList() {
    if (inList) { html += `</${inList}>`; inList = null; }
  }

  while (i < lines.length) {
    const line = lines[i];

    if (line.startsWith("```")) {
      closeList();
      const buf = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) { buf.push(lines[i]); i++; }
      html += `<pre><code>${escapeHtml(buf.join("\n"))}</code></pre>`;
      i++;
      continue;
    }

    if (/^\s*\|.+\|\s*$/.test(line) && lines[i + 1] && /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i + 1])) {
      closeList();
      const headCells = line.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
      i += 2;
      const rows = [];
      while (i < lines.length && /^\s*\|.+\|\s*$/.test(lines[i])) {
        rows.push(lines[i].trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim()));
        i++;
      }
      html += "<table><thead><tr>" + headCells.map((c) => `<th>${renderInline(c)}</th>`).join("") + "</tr></thead><tbody>";
      for (const r of rows) html += "<tr>" + r.map((c) => `<td>${renderInline(c)}</td>`).join("") + "</tr>";
      html += "</tbody></table>";
      continue;
    }

    const h = line.match(/^(#{2,4})\s+(.*)$/);
    if (h) {
      closeList();
      const level = Math.min(h[1].length + 2, 6);
      html += `<h${level}>${renderInline(h[2])}</h${level}>`;
      i++;
      continue;
    }

    const ol = line.match(/^\s*\d+\.\s+(.*)$/);
    const ul = line.match(/^\s*[-*]\s+(.*)$/);
    if (ol) {
      if (inList !== "ol") { closeList(); html += "<ol>"; inList = "ol"; }
      html += `<li>${renderInline(ol[1])}</li>`;
      i++;
      continue;
    }
    if (ul) {
      if (inList !== "ul") { closeList(); html += "<ul>"; inList = "ul"; }
      html += `<li>${renderInline(ul[1])}</li>`;
      i++;
      continue;
    }

    closeList();
    if (line.trim() === "") { i++; continue; }
    html += `<p>${renderInline(line)}</p>`;
    i++;
  }
  closeList();
  return html;
}

// ---------------------------------------------------------------- message rendering

function scrollToBottom() {
  chatScroll.scrollTop = chatScroll.scrollHeight;
}

function addMessage(role, initialHtml) {
  const wrap = document.createElement("div");
  wrap.className = "msg " + (role === "user" ? "msg-user" : "msg-agent");
  wrap.innerHTML = `<div class="avatar">${role === "user" ? "you" : "◈"}</div><div class="bubble">${initialHtml || ""}</div>`;
  chatScroll.appendChild(wrap);
  scrollToBottom();
  return wrap.querySelector(".bubble");
}

function sourcesHtml(sources) {
  if (!sources || sources.length === 0) return "";
  const items = sources
    .map((s) => `<li>${escapeHtml(s.title)} — ${escapeHtml(s.heading)} <span style="opacity:.6">(${Math.round(s.relevance * 100)}%)</span></li>`)
    .join("");
  return `<div class="sources"><div class="src-title">Consulted from the local knowledge base</div><ul>${items}</ul></div>`;
}

const MODE_LABEL = { llm: "local model", kb: "knowledge base (model offline)", tool: "local tool" };

// ---------------------------------------------------------------- sending

async function sendMessage(text) {
  if (sending) return;
  text = text.trim();
  if (!text) return;

  sending = true;
  sendBtn.disabled = true;
  input.value = "";
  input.style.height = "auto";

  addMessage("user", `<p>${renderInline(text)}</p>`);
  history.push({ role: "user", content: text });

  const bubble = addMessage("agent", '<span class="cursor"></span>');
  let raw = "";
  let meta = null;

  try {
    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, history: history.slice(0, -1) }),
    });

    if (!resp.ok || !resp.body) {
      const err = await resp.json().catch(() => ({}));
      bubble.innerHTML = `<p class="error-note">${escapeHtml(err.error || "Request failed (" + resp.status + ").")}</p>`;
      sending = false; sendBtn.disabled = false;
      return;
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      let idx;
      while ((idx = buf.indexOf("\n")) !== -1) {
        const line = buf.slice(0, idx);
        buf = buf.slice(idx + 1);
        if (!line.trim()) continue;
        const evt = JSON.parse(line);

        if (evt.type === "meta") {
          meta = evt;
        } else if (evt.type === "token") {
          raw += evt.text;
          const tag = meta ? `<span class="mode-tag">${MODE_LABEL[meta.mode] || meta.mode}</span>` : "";
          bubble.innerHTML = tag + renderMarkdown(raw) + '<span class="cursor"></span>';
          scrollToBottom();
        } else if (evt.type === "error") {
          raw += `\n\n*${evt.message}*`;
        } else if (evt.type === "done") {
          const tag = meta ? `<span class="mode-tag">${MODE_LABEL[meta.mode] || meta.mode}</span>` : "";
          bubble.innerHTML = tag + renderMarkdown(raw) + sourcesHtml(meta && meta.sources);
          scrollToBottom();
        }
      }
    }

    history.push({ role: "assistant", content: raw });
  } catch (e) {
    bubble.innerHTML += `<p class="error-note">Connection lost: ${escapeHtml(String(e.message || e))}</p>`;
  } finally {
    sending = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

composer.addEventListener("submit", (e) => {
  e.preventDefault();
  sendMessage(input.value);
});

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage(input.value);
  }
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 200) + "px";
});

document.querySelectorAll(".chip[data-prompt]").forEach((btn) => {
  btn.addEventListener("click", () => sendMessage(btn.dataset.prompt));
});
document.querySelectorAll(".chip[data-insert]").forEach((btn) => {
  btn.addEventListener("click", () => {
    input.value = btn.dataset.insert;
    input.focus();
    input.selectionStart = input.selectionEnd = input.value.length;
  });
});

document.getElementById("newChat").addEventListener("click", () => {
  history = [];
  document.querySelectorAll(".msg").forEach((el, idx) => { if (idx > 0) el.remove(); });
  input.focus();
});

// ---------------------------------------------------------------- status polling

async function pollHealth() {
  try {
    const resp = await fetch("/api/health");
    const data = await resp.json();
    const llm = data.llm || {};
    if (!llm.online) {
      llmStatusEl.innerHTML = '<span class="dot dot-bad"></span>Ollama not reachable';
    } else if (!llm.installed) {
      llmStatusEl.innerHTML = `<span class="dot dot-warn"></span>model "${escapeHtml(llm.model)}" not pulled`;
    } else {
      llmStatusEl.innerHTML = `<span class="dot dot-ok"></span>${escapeHtml(llm.model)} ready`;
    }
    const kb = data.knowledge || {};
    kbStatusEl.innerHTML = `<span class="dot dot-ok"></span>${kb.documents ?? 0} notes, ${kb.chunks ?? 0} sections`;
  } catch (e) {
    llmStatusEl.innerHTML = '<span class="dot dot-bad"></span>backend unreachable';
    kbStatusEl.innerHTML = '<span class="dot dot-bad"></span>backend unreachable';
  }
}

pollHealth();
setInterval(pollHealth, 15000);
