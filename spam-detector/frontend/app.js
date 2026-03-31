const apiBase = "/api";

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function setJson(elementId, data) {
  const el = document.getElementById(elementId);
  el.textContent = JSON.stringify(data, null, 2);
}

function setError(elementId, message) {
  const el = document.getElementById(elementId);
  el.innerHTML = `<div class="error">${escapeHtml(message)}</div>`;
}

function renderAnalysisResult(elementId, result) {
  const el = document.getElementById(elementId);
  if (!result || result.error) {
    setError(elementId, result?.error || "Unknown error");
    return;
  }

  const spamConf = typeof result.spam_confidence === "number" ? `${(result.spam_confidence * 100).toFixed(1)}%` : result.spam_confidence;
  const malConf = typeof result.malware_confidence === "number" ? `${(result.malware_confidence * 100).toFixed(1)}%` : result.malware_confidence;
  const label = result.label || (result.is_spam ? "Spam" : "Ham");

  el.innerHTML = `
    <div class="result-row"><span class="label">Classification:</span> <span class="value ${result.is_spam ? 'spam' : 'ham'}">${escapeHtml(label)}</span></div>
    <div class="result-row"><span class="label">Spam Detected:</span> <span class="value">${escapeHtml(result.is_spam)}</span></div>
    <div class="result-row"><span class="label">Spam Confidence:</span> <span class="value">${escapeHtml(spamConf)}</span></div>
    <hr style="margin: 10px 0; border: 0; border-top: 1px solid #ccc;">
    <div class="result-row"><span class="label">Malware Detected:</span> <span class="value ${result.is_malware ? 'malware' : 'safe'}">${escapeHtml(result.is_malware ? 'YES - DANGER' : 'No')}</span></div>
    <div class="result-row"><span class="label">Malware Confidence:</span> <span class="value">${escapeHtml(malConf)}</span></div>
  `;
}

async function fetchJson(url, options) {
  const resp = await fetch(url, options);
  const text = await resp.text();

  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    // Non-JSON response (e.g., plain text or HTML)
    data = null;
  }

  if (!resp.ok) {
    const message = data?.error || data?.message || text || `HTTP ${resp.status}`;
    throw new Error(message);
  }

  return data;
}

async function analyzeText(event) {
  event.preventDefault();
  const text = document.getElementById("email-text").value.trim();
  if (!text) {
    setError("text-result", "Please paste a message first.");
    return;
  }

  try {
    const result = await fetchJson(`${apiBase}/analyze-text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email_text: text }),
    });

    renderAnalysisResult("text-result", result);
  } catch (err) {
    setError("text-result", err.message || "Request failed");
  }
}

async function analyzeFile(event) {
  event.preventDefault();
  const input = document.getElementById("email-file");
  const file = input.files && input.files[0];
  if (!file) {
    setError("file-result", "Please select a file to upload.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const result = await fetchJson(`${apiBase}/analyze-file`, {
      method: "POST",
      body: formData,
    });

    renderAnalysisResult("file-result", result);
  } catch (err) {
    setError("file-result", err.message || "Request failed");
  }
}

function init() {
  document.getElementById("text-form").addEventListener("submit", analyzeText);
  document.getElementById("file-form").addEventListener("submit", analyzeFile);
}

document.addEventListener("DOMContentLoaded", init);
