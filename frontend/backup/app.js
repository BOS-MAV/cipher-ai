const button = document.getElementById("askButton");
const questionEl = document.getElementById("question");
const statusEl = document.getElementById("status");
const answerCard = document.getElementById("answerCard");
const answerEl = document.getElementById("answer");
const toolsEl = document.getElementById("tools");
const toolDetails = document.getElementById("toolDetails");

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderText(value) {
  return escapeHtml(value).replaceAll("\n", "<br>");
}

async function askCipher() {
  const question = questionEl.value.trim();
  if (!question) return;

  button.disabled = true;
  statusEl.textContent = "Searching CIPHER…";
  answerCard.hidden = true;

  try {
    const response = await fetch(`${window.CIPHER_AI_API_BASE}/api/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    let data = {};
    try { data = await response.json(); } catch (_) {}
    if (!response.ok) {
      throw new Error(data.detail || `Request failed (${response.status})`);
    }

    answerEl.innerHTML = renderText(data.answer || "No answer returned.");
    toolsEl.textContent = JSON.stringify(data.tools_used || [], null, 2);
    toolDetails.hidden = !(data.tools_used && data.tools_used.length);
    answerCard.hidden = false;
    statusEl.textContent = "";
  } catch (error) {
    answerEl.textContent = error.message;
    toolsEl.textContent = "";
    toolDetails.hidden = true;
    answerCard.hidden = false;
    statusEl.textContent = "";
  } finally {
    button.disabled = false;
  }
}

button.addEventListener("click", askCipher);
questionEl.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") askCipher();
});
