const statusEl = document.getElementById("status");
const statusLabel = statusEl.querySelector(".status-label");
const questionEl = document.getElementById("question");
const runEl = document.getElementById("run");
const hintEl = document.getElementById("hint");
const emptyEl = document.getElementById("empty");
const workEl = document.getElementById("work");
const subsEl = document.getElementById("subs");
const answerEl = document.getElementById("answer");
const sourcesEl = document.getElementById("sources");

function setStatus(kind, label) {
  statusEl.className = `status ${kind}`;
  statusLabel.textContent = label;
}

async function refreshStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    if (data.ready) {
      setStatus("ready", "Index ready");
      return;
    }
    if (data.error) {
      setStatus("error", "Init failed");
      hintEl.textContent = data.error;
      return;
    }
    setStatus("busy", "Warming index");
  } catch {
    setStatus("error", "Offline");
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function showError(message) {
  emptyEl.classList.remove("hidden");
  workEl.classList.add("hidden");
  emptyEl.innerHTML = `<p class="section-label">02 / Output</p><div class="error-box">${escapeHtml(message)}</div>`;
}

function renderResult(data) {
  emptyEl.classList.add("hidden");
  workEl.classList.remove("hidden");
  subsEl.innerHTML = data.sub_questions
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
  answerEl.textContent = data.answer;
  sourcesEl.innerHTML = data.sources
    .map(
      (src) => `
        <article class="source">
          <a href="${escapeHtml(src.source)}" target="_blank" rel="noopener noreferrer">${escapeHtml(src.title)}</a>
          <p>${escapeHtml(src.snippet)}</p>
        </article>`
    )
    .join("");
}

async function runPipeline() {
  const question = questionEl.value.trim();
  if (question.length < 8) {
    showError("Write a question of at least 8 characters.");
    return;
  }

  runEl.disabled = true;
  setStatus("busy", "Running");
  hintEl.textContent = "Planning, retrieving, and answering…";

  try {
    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const payload = await res.json();
    if (!res.ok) {
      const detail = payload.detail || payload.error || "Request failed.";
      throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }
    renderResult(payload);
    setStatus("ready", "Complete");
    hintEl.textContent = "Run another question against the same index.";
  } catch (err) {
    showError(err.message);
    setStatus("error", "Failed");
  } finally {
    runEl.disabled = false;
  }
}

runEl.addEventListener("click", runPipeline);
questionEl.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
    runPipeline();
  }
});

document.getElementById("chips").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-query]");
  if (!button) return;
  questionEl.value = button.dataset.query;
  questionEl.focus();
});

refreshStatus();
setInterval(refreshStatus, 4000);
