/**
 * Antigravity 2.0 Webview Client.
 * Connects to the ASGI backend, streams SDLC lifecycle events, and manages the 3-column UI.
 */

// XSS Sanitization utility (AC-Sec-1)
function escapeHtml(unsafeText) {
  if (typeof unsafeText !== "string") return "";
  return unsafeText
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

let ws = null;
let currentAgentMessageEl = null;

function initTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabBtns.forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));

      btn.classList.add("active");
      const targetId = `tab-content-${btn.getAttribute("data-tab")}`;
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add("active");
      }
    });
  });
}

async function loadStatusAndSkills() {
  try {
    const resStatus = await fetch("/api/status");
    if (resStatus.ok) {
      const data = await resStatus.json();
      document.getElementById("workspace-label").textContent = escapeHtml(data.workspace);
      document.getElementById("branch-label").textContent = escapeHtml(data.branch);
      const shield = document.getElementById("stash-shield-status");
      shield.textContent = data.is_clean ? "🛡️ Clean" : "⚠️ Dirty";
      shield.className = `status-badge ${data.is_clean ? "clean" : "dirty"}`;
    }

    const resSkills = await fetch("/api/skills");
    if (resSkills.ok) {
      const data = await resSkills.json();
      const listEl = document.getElementById("skills-list");
      listEl.innerHTML = "";
      data.skills.forEach((skill) => {
        const item = document.createElement("div");
        item.className = "skill-badge";
        item.innerHTML = `
          <span class="badge-name">${escapeHtml(skill.name)}</span>
          <span class="badge-layer">${escapeHtml(skill.layer)}</span>
        `;
        listEl.appendChild(item);
      });
    }

    const resDiff = await fetch("/api/diff");
    if (resDiff.ok) {
      const diffData = await resDiff.json();
      document.getElementById("diff-viewer").textContent = diffData.diff || "(No working tree modifications)";
    }
  } catch (err) {
    console.error("Failed to load workspace status:", err);
  }
}

function connectWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/sdlc`;
  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log("WebSocket connected to SDLC harness");
  };

  ws.onmessage = (event) => {
    let msg;
    try {
      msg = JSON.parse(event.data);
    } catch (e) {
      console.error("Non-JSON WebSocket message received:", event.data);
      return;
    }

    const eventType = msg.event;
    switch (eventType) {
      case "stage_changed":
        handleStageChanged(msg.stage);
        break;
      case "token":
        handleToken(msg.content);
        break;
      case "approval_required":
        handleApprovalRequired(msg.spec_content);
        break;
      case "tdd_output":
        handleTddOutput(msg.returncode, msg.output);
        break;
      case "completed":
        handleCompleted(msg.pr_content);
        break;
      case "error":
        handleError(msg.message);
        break;
      default:
        console.log("Unhandled event:", msg);
    }
  };

  ws.onclose = () => {
    console.log("WebSocket disconnected. Reconnecting in 3s...");
    setTimeout(connectWebSocket, 3000);
  };
}

function handleStageChanged(stage) {
  document.getElementById("active-stage-pill").textContent = escapeHtml(stage);
  appendChatEvent(`Fase activa: ${stage}`, "agent");
  currentAgentMessageEl = null;
}

function handleToken(tokenContent) {
  if (!currentAgentMessageEl) {
    currentAgentMessageEl = document.createElement("div");
    currentAgentMessageEl.className = "message-bubble agent";
    document.getElementById("chat-messages").appendChild(currentAgentMessageEl);
  }
  currentAgentMessageEl.innerHTML += escapeHtml(tokenContent);
  const container = document.getElementById("chat-messages");
  container.scrollTop = container.scrollHeight;
}

function handleApprovalRequired(specContent) {
  document.getElementById("approval-bar").classList.add("active");
  document.getElementById("artifacts-viewer").textContent = specContent;
  
  // Switch auxiliary tab to artifacts
  const artifactsBtn = document.querySelector('[data-tab="artifacts"]');
  if (artifactsBtn) artifactsBtn.click();
}

function handleTddOutput(returncode, output) {
  const tddViewer = document.getElementById("tdd-viewer");
  tddViewer.textContent += `\n[Exit Code: ${returncode}]\n${output}\n`;
}

function handleCompleted(prContent) {
  document.getElementById("artifacts-viewer").textContent = prContent;
  appendChatEvent("🚀 Ejecución completada. Todos los quality gates superados.", "agent");
}

function handleError(errorMessage) {
  appendChatEvent(`❌ Error: ${errorMessage}`, "agent");
}

function appendChatEvent(text, sender) {
  const bubble = document.createElement("div");
  bubble.className = `message-bubble ${sender}`;
  bubble.innerHTML = escapeHtml(text);
  document.getElementById("chat-messages").appendChild(bubble);
  const container = document.getElementById("chat-messages");
  container.scrollTop = container.scrollHeight;
}

function initActionButtons() {
  document.getElementById("btn-approve").addEventListener("click", () => {
    document.getElementById("approval-bar").classList.remove("active");
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action: "approval_response", approved: true }));
    }
    appendChatEvent("✅ Especificación aprobada por el operador humano.", "user");
  });

  document.getElementById("btn-revise").addEventListener("click", () => {
    document.getElementById("approval-bar").classList.remove("active");
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action: "approval_response", approved: false, feedback: "Revisión solicitada." }));
    }
    appendChatEvent("🛑 Especificación rechazada para revisión.", "user");
  });

  document.getElementById("task-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const input = document.getElementById("task-input");
    const task = input.value.trim();
    if (!task) return;

    const provider = document.getElementById("provider-select").value;
    const model = document.getElementById("model-select").value;

    appendChatEvent(task, "user");
    input.value = "";

    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action: "start", task, provider, model }));
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  loadStatusAndSkills();
  initActionButtons();
  connectWebSocket();
});
