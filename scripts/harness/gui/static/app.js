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
let currentRawContent = "";

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

function renderDiff(diffText) {
  const viewer = document.getElementById("diff-viewer");
  if (!viewer) return;
  if (!diffText || !diffText.trim()) {
    viewer.textContent = "(Sin modificaciones en el working tree)";
    return;
  }
  const lines = diffText.split("\n");
  viewer.innerHTML = "";
  lines.forEach((line) => {
    const div = document.createElement("div");
    if (line.startsWith("+") && !line.startsWith("+++")) {
      div.className = "diff-line-add";
    } else if (line.startsWith("-") && !line.startsWith("---")) {
      div.className = "diff-line-del";
    } else if (line.startsWith("@@")) {
      div.className = "diff-line-hunk";
    }
    div.textContent = line;
    viewer.appendChild(div);
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
          <div class="skill-badge-header">
            <span class="badge-name">${escapeHtml(skill.name)}</span>
            <span class="badge-layer">${escapeHtml(skill.layer)}</span>
          </div>
        `;
        listEl.appendChild(item);
      });
    }

    const resDiff = await fetch("/api/diff");
    if (resDiff.ok) {
      const diffData = await resDiff.json();
      renderDiff(diffData.diff || "");
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
  const pill = document.getElementById("active-stage-pill");
  if (pill) {
    pill.innerHTML = `<span class="status-dot"></span><span>${escapeHtml(stage)}</span>`;
  }
  appendChatEvent(`Fase activa: ${stage}`, "agent");
  currentAgentMessageEl = null;
  currentRawContent = "";
}

function handleToken(tokenContent) {
  if (!currentAgentMessageEl) {
    const row = document.createElement("div");
    row.className = "message-row agent";
    row.innerHTML = `
      <div class="message-avatar agent-avatar">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
        </svg>
      </div>
      <div class="message-bubble agent"></div>
    `;
    document.getElementById("chat-messages").appendChild(row);
    currentAgentMessageEl = row.querySelector(".message-bubble");
    currentRawContent = "";
  }
  currentRawContent += tokenContent;
  if (window.marked && typeof marked.parse === "function") {
    currentAgentMessageEl.innerHTML = marked.parse(currentRawContent);
  } else {
    currentAgentMessageEl.innerHTML = escapeHtml(currentRawContent);
  }
  const container = document.getElementById("chat-messages");
  container.scrollTop = container.scrollHeight;
}

function handleApprovalRequired(specContent) {
  document.getElementById("approval-bar").classList.add("active");
  const artifactsViewer = document.getElementById("artifacts-viewer");
  if (window.marked && typeof marked.parse === "function") {
    artifactsViewer.innerHTML = marked.parse(specContent);
  } else {
    artifactsViewer.textContent = specContent;
  }
  
  // Switch auxiliary tab to artifacts
  const artifactsBtn = document.querySelector('[data-tab="artifacts"]');
  if (artifactsBtn) artifactsBtn.click();
}

function handleTddOutput(returncode, output) {
  const tddViewer = document.getElementById("tdd-viewer");
  tddViewer.textContent += `\n[Exit Code: ${returncode}]\n${output}\n`;
}

function handleCompleted(prContent) {
  const artifactsViewer = document.getElementById("artifacts-viewer");
  if (window.marked && typeof marked.parse === "function") {
    artifactsViewer.innerHTML = marked.parse(prContent);
  } else {
    artifactsViewer.textContent = prContent;
  }
  appendChatEvent("🚀 Ejecución completada. Todos los quality gates superados.", "agent");
}

function handleError(errorMessage) {
  appendChatEvent(`❌ Error: ${errorMessage}`, "agent");
}

function appendChatEvent(text, sender) {
  const row = document.createElement("div");
  row.className = `message-row ${sender}`;
  
  const avatar = document.createElement("div");
  avatar.className = `message-avatar ${sender}-avatar`;
  if (sender === "user") {
    avatar.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`;
  } else {
    avatar.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`;
  }

  const bubble = document.createElement("div");
  bubble.className = `message-bubble ${sender}`;
  if (sender === "agent" && window.marked && typeof marked.parse === "function") {
    bubble.innerHTML = marked.parse(text);
  } else {
    bubble.innerHTML = escapeHtml(text);
  }

  row.appendChild(avatar);
  row.appendChild(bubble);
  document.getElementById("chat-messages").appendChild(row);
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

  const refreshDiffBtn = document.getElementById("btn-refresh-diff");
  if (refreshDiffBtn) {
    refreshDiffBtn.addEventListener("click", async () => {
      try {
        const resDiff = await fetch("/api/diff");
        if (resDiff.ok) {
          const diffData = await resDiff.json();
          renderDiff(diffData.diff || "");
        }
      } catch (e) {
        console.error("Error refreshing diff:", e);
      }
    });
  }

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
