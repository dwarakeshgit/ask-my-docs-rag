"use strict";

/* ===== Config ===== */
const API_BASE_URL = "http://127.0.0.1:8000"; // change to your Render URL when deployed
const ENDPOINTS = {
  documents: `${API_BASE_URL}/documents/`,
  upload: `${API_BASE_URL}/upload/`,
  ask: `${API_BASE_URL}/ask/`,
};
const ALLOWED_EXT = ["pdf","docx","txt","md","markdown","csv","xlsx","xls","pptx","html","htm"];

/* ===== DOM ===== */
const $ = (id) => document.getElementById(id);
const el = (tag, cls, text) => {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined) node.textContent = text;
  return node;
};
const dom = {
  sidebar: $("sidebar"), scrim: $("scrim"), menuBtn: $("menuBtn"),
  chatScroll: $("chatScroll"), empty: $("emptyState"), messages: $("messages"),
  form: $("askForm"), input: $("questionInput"), send: $("sendBtn"),
  docList: $("docList"), docCount: $("docCount"), navCount: $("navCount"),
  dropzone: $("dropzone"), dropTitle: $("dropTitle"), upStatus: $("upStatus"), upLabel: $("upLabel"), upPct: $("upPct"), upName: $("upName"), fileInput: $("fileInput"), progress: $("progress"), progressBar: $("progressBar"),
  refresh: $("refreshBtn"), uploadBtn: $("uploadBtn"), toasts: $("toasts"),
};
let isAsking = false;
let knownDocs = null; // filenames from the previous list, used to animate newly indexed cards

/* ===== API ===== */
async function apiRequest(url, options) {
  let response;
  try {
    response = await fetch(url, options);
  } catch {
    setStatus(false);
    throw new Error("Can't reach the backend. Check that the server is running at " + API_BASE_URL + ".");
  }
  setStatus(true);
  let data = null;
  try { data = await response.json(); } catch { /* non-JSON body */ }
  if (!response.ok) throw new Error(extractError(data, response.status));
  if (data === null) throw new Error("The server returned an invalid response.");
  return data;
}

function extractError(data, status) {
  const detail = data && data.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0] && detail[0].msg) return detail[0].msg;
  return `Request failed (HTTP ${status}).`;
}

const fetchDocuments = () => apiRequest(ENDPOINTS.documents);
const askQuestion = (question) => apiRequest(ENDPOINTS.ask, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ question }),
});

function uploadFile(file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const body = new FormData();
    body.append("file", file);
    xhr.open("POST", ENDPOINTS.upload);
    xhr.upload.onprogress = (e) => e.lengthComputable && onProgress(e.loaded / e.total);
    xhr.onerror = () => { setStatus(false); reject(new Error("Can't reach the backend. Check that the server is running.")); };
    xhr.onload = () => {
      let data = null;
      try { data = JSON.parse(xhr.responseText); } catch { /* ignore */ }
      if (xhr.status >= 200 && xhr.status < 300 && data) resolve(data);
      else reject(new Error(extractError(data, xhr.status)));
    };
    xhr.send(body);
  });
}

/* ===== Status ===== */
function setStatus(online) {
  document.querySelectorAll(".status").forEach((node) => {
    node.querySelector(".dot").className = "dot " + (online ? "online" : "offline");
    node.querySelector(".status-text").textContent = online ? "RAG System Online" : "Backend Offline";
  });
}

/* ===== Toasts ===== */
function toast(type, title, text, duration = 4500) {
  const node = el("div", `toast ${type}`);
  const body = el("div");
  body.append(el("div", "toast-title", title));
  if (text) body.append(el("div", "toast-text", text));
  node.append(body);
  dom.toasts.append(node);
  setTimeout(() => { node.classList.add("out"); setTimeout(() => node.remove(), 220); }, duration);
}

/* ===== Navigation ===== */
function showView(name) {
  document.querySelectorAll(".view").forEach((v) => (v.hidden = v.id !== `view-${name}`));
  document.querySelectorAll(".nav-item").forEach((b) => b.classList.toggle("active", b.dataset.view === name));
  toggleDrawer(false);
  if (name === "documents") loadDocuments();
  else dom.input.focus();
}
function toggleDrawer(open) {
  dom.sidebar.classList.toggle("open", open);
  dom.scrim.hidden = !open;
  dom.menuBtn.setAttribute("aria-expanded", String(open));
}

/* ===== Documents ===== */
function renderDocuments(data) {
  const docs = Array.isArray(data.documents) ? data.documents : null;
  if (!docs) throw new Error("The server returned an invalid response.");
  const count = typeof data.count === "number" ? data.count : docs.length;
  dom.docCount.textContent = `${count} document${count === 1 ? "" : "s"} indexed`;
  dom.navCount.textContent = count;
  dom.navCount.hidden = false;
  $("statDocs").textContent = count;
  $("statChunks").textContent = docs.reduce((sum, d) => sum + (Number(d.chunks) || 0), 0);
  $("statTypes").textContent = new Set(docs.map((d) => String(d.file_type).toLowerCase())).size;
  dom.docList.replaceChildren();
  if (!docs.length) {
    dom.docList.append(el("li", "list-empty", "No documents yet. Upload one to get started."));
    return;
  }
  docs.forEach((doc) => {
    const type = String(doc.file_type || "").toLowerCase();
    const isNew = knownDocs !== null && !knownDocs.has(doc.filename);
    const li = el("li", "doc-card" + (isNew ? " is-new" : ""));
    li.append(el("div", `doc-type ${type}`, type.toUpperCase() || "FILE"));
    const info = el("div", "doc-info");
    const name = el("div", "doc-name", doc.filename);
    name.title = doc.filename;
    const meta = el("div", "doc-meta");
    meta.append(el("span", "", `${doc.chunks} chunk${doc.chunks === 1 ? "" : "s"}`), el("span", "doc-status", "Indexed"));
    info.append(name, meta);
    li.append(info);
    dom.docList.append(li);
  });
  knownDocs = new Set(docs.map((d) => d.filename));
}

async function loadDocuments() {
  dom.docList.replaceChildren(el("li", "skeleton"), el("li", "skeleton"));
  try {
    renderDocuments(await fetchDocuments());
  } catch (err) {
    dom.docList.replaceChildren(el("li", "list-empty", "Couldn't load documents."));
    dom.docCount.textContent = "Unavailable";
    toast("error", "Couldn't load documents", err.message);
  }
}

/* ===== Upload ===== */
let upHideTimer = null;
function setDrag(on) {
  dom.dropzone.classList.toggle("drag", on);
  dom.dropTitle.textContent = on ? "Drop your document here" : "Drop documents here";
}
function setUpload(state, label, name, pct) {
  clearTimeout(upHideTimer);
  dom.upStatus.hidden = false;
  dom.upStatus.dataset.state = state;
  dom.upLabel.textContent = label;
  dom.upName.textContent = name;
  dom.upPct.textContent = pct === null ? "" : `${pct}%`;
  dom.progressBar.classList.toggle("indet", state === "indexing");
  if (pct !== null) dom.progressBar.style.width = `${pct}%`;
}
function flashDropzone(cls, ms) {
  dom.dropzone.classList.remove("success", "error");
  void dom.dropzone.offsetWidth; // restart the animation
  dom.dropzone.classList.add(cls);
  setTimeout(() => dom.dropzone.classList.remove(cls), ms);
}
function hideUploadLater(ms) {
  upHideTimer = setTimeout(() => { dom.upStatus.hidden = true; }, ms);
}

async function handleFiles(fileList) {
  const files = Array.from(fileList);
  if (!files.length) return;
  dom.dropzone.classList.add("busy");
  for (const file of files) {
    const ext = file.name.split(".").pop().toLowerCase();
    if (!ALLOWED_EXT.includes(ext)) {
      toast("error", "Unsupported file", `${file.name} isn't a supported format.`);
      setUpload("error", "Unsupported file type", file.name, null);
      flashDropzone("error", 700);
      hideUploadLater(3500);
      continue;
    }
    setUpload("uploading", "Uploading document...", file.name, 0);
    try {
      const result = await uploadFile(file, (ratio) => {
        const pct = Math.round(ratio * 100);
        if (ratio >= 1) setUpload("indexing", "Indexing document...", file.name, null); // server is processing
        else setUpload("uploading", "Uploading document...", file.name, pct);
      });
      setUpload("success", "✓ Upload complete", result.filename || file.name, 100);
      flashDropzone("success", 1800);
      toast("success", "Upload complete", `${result.filename || file.name} · ${result.chunks_indexed} chunks indexed`);
      await loadDocuments();
      hideUploadLater(2500);
    } catch (err) {
      setUpload("error", "Upload failed", file.name, null);
      flashDropzone("error", 700);
      toast("error", `Upload failed: ${file.name}`, err.message);
      hideUploadLater(4000);
    }
  }
  dom.dropzone.classList.remove("busy");
  dom.fileInput.value = "";
}

/* ===== Chat ===== */
const FILE_ICON = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/></svg>';

function parseCitation(text) {
  const match = String(text).match(/^(.*?),\s*(Page\s*.+)$/i);
  return match ? { name: match[1], page: match[2] } : { name: String(text), page: "" };
}

function addUserMessage(text) {
  dom.empty.hidden = true;
  dom.messages.append(el("div", "msg user", text));
  scrollChat();
}

function addBotMessage() {
  const wrap = el("div", "msg bot");
  wrap.append(el("div", "avatar", "A"));
  const body = el("div", "bot-body");
  wrap.append(body);
  dom.messages.append(wrap);
  scrollChat();
  return body;
}

function renderLoading(body) {
  body.replaceChildren();
  const row = el("div", "loading");
  row.dataset.stage = "search";
  const visual = el("div", "ld-visual");
  visual.innerHTML = '<div class="ld-doc"><i class="ld-scan"></i></div>' +
    '<div class="ld-orb"><i class="ld-ring"></i><i class="ld-core"></i><i class="ld-p p1"></i><i class="ld-p p2"></i><i class="ld-p p3"></i></div>';
  const label = el("span", "ld-label", "Searching your documents...");
  row.append(visual, label);
  body.append(row);
  // Visual stage switch only; the answer itself is never produced client-side.
  const timer = setTimeout(() => {
    row.dataset.stage = "generate";
    label.textContent = "Generating grounded answer...";
  }, 2500);
  return () => clearTimeout(timer);
}

function renderAnswer(body, data) {
  if (typeof data.answer !== "string") throw new Error("The server returned an invalid response.");
  body.replaceChildren(el("div", "ans-label", "AI ANSWER"));
  const refused = data.sufficient === false;
  const answer = el("div", "answer" + (refused ? " refusal" : ""), data.answer.trim() ||
    "I don't have enough information in the provided documents to answer that.");
  const citations = Array.isArray(data.citations) ? data.citations : [];
  if (citations.length) {
    // Badges mirror the backend citations array order exactly.
    const cites = el("span", "cites");
    citations.forEach((_, i) => {
      const badge = el("button", "cite-badge", `[${i + 1}]`);
      badge.type = "button";
      badge.setAttribute("aria-label", `Go to source ${i + 1}`);
      badge.addEventListener("click", () => highlightSource(body, i));
      cites.append(badge);
    });
    answer.append(" ", cites);
  }
  body.append(answer);
  if (refused && data.reason) body.append(el("div", "reason", data.reason));
  if (citations.length) {
    const sources = el("div", "sources");
    sources.append(el("div", "sources-title", "Sources"));
    const list = el("div", "source-list");
    citations.forEach((c, i) => {
      const { name, page } = parseCitation(c);
      const ext = (name.split(".").pop() || "").toLowerCase();
      const card = el("div", `source t-${ext}`);
      card.dataset.index = i;
      card.append(el("span", "src-num", `[${i + 1}]`));
      card.insertAdjacentHTML("beforeend", FILE_ICON);
      const text = el("div", "source-text");
      const line = el("div", "source-name", name);
      if (page) line.append(el("span", "source-page", ` — ${page}`));
      text.append(line);
      card.append(text);
      list.append(card);
    });
    sources.append(list);
    body.append(sources);
  }
}

function highlightSource(body, index) {
  const card = body.querySelector(`.source[data-index="${index}"]`);
  if (!card) return;
  card.scrollIntoView({ block: "nearest", behavior: "smooth" });
  card.classList.remove("hl");
  void card.offsetWidth;
  card.classList.add("hl");
  setTimeout(() => card.classList.remove("hl"), 1400);
}

function renderError(body, message) {
  body.replaceChildren(el("div", "answer error-msg", message));
}

function scrollChat() {
  dom.chatScroll.scrollTo({ top: dom.chatScroll.scrollHeight, behavior: "smooth" });
}

function setAsking(state) {
  isAsking = state;
  dom.input.disabled = state;
  dom.send.disabled = state;
  if (!state) dom.input.focus();
}

async function handleAsk() {
  const question = dom.input.value.trim();
  if (isAsking) return;
  if (!question) { toast("error", "Enter a question", "Type a question about your documents first."); return; }
  addUserMessage(question);
  dom.input.value = "";
  autoGrow();
  setAsking(true);
  const body = addBotMessage();
  const stopTimer = renderLoading(body);
  try {
    renderAnswer(body, await askQuestion(question));
  } catch (err) {
    renderError(body, err.message);
    toast("error", "Couldn't get an answer", err.message);
  } finally {
    stopTimer();
    setAsking(false);
    scrollChat();
  }
}

function autoGrow() {
  dom.input.style.height = "auto";
  dom.input.style.height = Math.min(dom.input.scrollHeight, 160) + "px";
}

/* ===== Events ===== */
document.querySelectorAll(".nav-item").forEach((b) => b.addEventListener("click", () => showView(b.dataset.view)));
document.querySelectorAll(".chip").forEach((c) => c.addEventListener("click", () => {
  if (isAsking) return;
  dom.input.value = c.dataset.q;
  handleAsk(); // same flow as the Send button
}));
dom.menuBtn.addEventListener("click", () => toggleDrawer(true));
dom.scrim.addEventListener("click", () => toggleDrawer(false));
dom.form.addEventListener("submit", (e) => { e.preventDefault(); handleAsk(); });
dom.input.addEventListener("input", autoGrow);
dom.input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); handleAsk(); }
});
dom.refresh.addEventListener("click", loadDocuments);
dom.uploadBtn.addEventListener("click", () => dom.fileInput.click());
dom.dropzone.addEventListener("click", () => dom.fileInput.click());
dom.dropzone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); dom.fileInput.click(); }
});
dom.fileInput.addEventListener("change", () => handleFiles(dom.fileInput.files));
["dragenter", "dragover"].forEach((t) => dom.dropzone.addEventListener(t, (e) => { e.preventDefault(); setDrag(true); }));
["dragleave", "drop"].forEach((t) => dom.dropzone.addEventListener(t, (e) => { e.preventDefault(); setDrag(false); }));
dom.dropzone.addEventListener("drop", (e) => handleFiles(e.dataTransfer.files));
document.addEventListener("keydown", (e) => e.key === "Escape" && toggleDrawer(false));

/* ===== Init ===== */
fetchDocuments().then(renderDocuments).catch((err) => toast("error", "Backend unavailable", err.message));
