/**
 * k-method app - Antigravity IDE Studio Client.
 * Connects to ASGI backend, streams SDLC lifecycle events, and manages the Antigravity UI.
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

const DEFAULT_PROVIDER_MODELS = {
  antigravity: [
    { id: "gemini-2.5-flash", name: "Gemini 2.5 Flash", default: true },
    { id: "gemini-2.5-pro", name: "Gemini 2.5 Pro" },
    { id: "gemini-2.0-flash", name: "Gemini 2.0 Flash" },
    { id: "gemini-1.5-pro", name: "Gemini 1.5 Pro" },
    { id: "gemini-3.8-flash", name: "Gemini 3.8 Flash High" },
  ],
  copilot: [
    { id: "auto", name: "Copilot Auto", default: true },
    { id: "gpt-4o", name: "GPT-4o (GitHub Copilot CLI)" },
    { id: "claude-3.5-sonnet", name: "Claude 3.5 Sonnet" },
    { id: "claude-3.7-sonnet", name: "Claude 3.7 Sonnet" },
    { id: "o3-mini", name: "o3-mini (Reasoning)" },
    { id: "gpt-6-luna", name: "GPT-6 Luna" },
  ],
  mock: [
    { id: "mock-model", name: "Mock Model (Offline)", default: true },
  ],
};

let availableProviderModels = DEFAULT_PROVIDER_MODELS;
let currentProvider = "antigravity";
let currentModel = "gemini-2.5-flash";
let autoApprove = false;
let ws = null;
let currentAgentBubble = null;
let currentRawContent = "";
let currentStepCard = null;

// ===================================================================
// Model Selection & SDK Discovery (AC-6, AC-7)
// ===================================================================

function updateModelOptions(selectedProvider, preselectedModel = null) {
  currentProvider = selectedProvider;
  const modelSelect = document.getElementById("model-select");
  const models = (availableProviderModels && availableProviderModels[selectedProvider]) ||
                 DEFAULT_PROVIDER_MODELS[selectedProvider] || [];

  if (modelSelect) {
    modelSelect.innerHTML = "";
    models.forEach((m) => {
      const opt = document.createElement("option");
      opt.value = m.id;
      opt.textContent = m.name || m.id;
      if (preselectedModel ? m.id === preselectedModel : m.default) {
        opt.selected = true;
        currentModel = m.id;
      }
      modelSelect.appendChild(opt);
    });

    const customOpt = document.createElement("option");
    customOpt.value = "__custom__";
    customOpt.textContent = "✍️ Personalizado...";
    modelSelect.appendChild(customOpt);
  }

  // Update Floating Pill Label
  const pillLabel = document.getElementById("model-pill-label");
  if (pillLabel) {
    const activeM = models.find(m => m.id === currentModel);
    pillLabel.textContent = activeM ? (activeM.name || activeM.id) : (preselectedModel || "Gemini 2.5 Flash");
  }

  renderPickerModelList(selectedProvider);
}

function renderPickerModelList(prov) {
  const container = document.getElementById("picker-models-list");
  if (!container) return;

  const models = (availableProviderModels && availableProviderModels[prov]) ||
                 DEFAULT_PROVIDER_MODELS[prov] || [];

  container.innerHTML = "";
  models.forEach((m) => {
    const row = document.createElement("div");
    row.className = `model-option-row ${m.id === currentModel ? "selected" : ""}`;
    row.innerHTML = `
      <span>${escapeHtml(m.name || m.id)}</span>
      ${m.default ? '<span style="font-size:0.7rem; color:var(--text-muted);">(Default)</span>' : ''}
    `;
    row.addEventListener("click", () => {
      currentModel = m.id;
      currentProvider = prov;
      const provSelect = document.getElementById("provider-select");
      if (provSelect) provSelect.value = prov;
      updateModelOptions(prov, m.id);
      document.getElementById("model-picker-card").classList.add("hidden");
    });
    container.appendChild(row);
  });
}

// ===================================================================
// Step Cards & Antigravity Activity Rendering
// ===================================================================

function createStepCard(title, isRunning = true) {
  const card = document.createElement("div");
  card.className = "antigravity-step-card open";
  card.innerHTML = `
    <div class="step-card-header">
      <div class="step-header-left">
        <span class="step-status-icon ${isRunning ? "running" : "success"}">
          ${isRunning ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>' : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>'}
        </span>
        <span class="step-card-title">${escapeHtml(title)}</span>
      </div>
      <svg class="step-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
    </div>
    <div class="step-card-content">
      <div class="step-sublist"></div>
    </div>
  `;

  card.querySelector(".step-card-header").addEventListener("click", () => {
    card.classList.toggle("open");
  });

  const chatContainer = document.getElementById("chat-messages");
  if (chatContainer) {
    chatContainer.appendChild(card);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }
  return card;
}

function addSubStepToCard(card, text) {
  if (!card) return;
  const list = card.querySelector(".step-sublist");
  if (!list) return;

  const item = document.createElement("div");
  item.className = "step-subitem";
  item.innerHTML = `
    <span class="step-subitem-icon">&bull;</span>
    <span>${escapeHtml(text)}</span>
  `;
  list.appendChild(item);

  const chatContainer = document.getElementById("chat-messages");
  if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight;
}

function finishStepCard(card, finalTitle) {
  if (!card) return;
  const icon = card.querySelector(".step-status-icon");
  if (icon) {
    icon.className = "step-status-icon success";
    icon.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>';
  }
  if (finalTitle) {
    const t = card.querySelector(".step-card-title");
    if (t) t.textContent = finalTitle;
  }
}

// ===================================================================
// WebSocket & SDLC Streaming Protocol (AC-3, AC-4, AC-5)
// ===================================================================

function connectWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/sdlc`;
  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log("Connected to k-method SDLC engine via WebSocket.");
  };

  ws.onmessage = (event) => {
    let msg;
    try {
      msg = JSON.parse(event.data);
    } catch (e) {
      console.error("Non-JSON message:", event.data);
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
        handleApprovalRequired(msg.spec_content, msg.spec_file);
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
    setTimeout(connectWebSocket, 3000);
  };
}

function handleStageChanged(stage) {
  const pill = document.getElementById("active-stage-pill");
  if (pill) {
    pill.innerHTML = `<span class="status-dot"></span><span>${escapeHtml(stage)}</span>`;
  }

  // Update Breadcrumb conversation title
  const breadcrumb = document.getElementById("breadcrumb-conversation");
  if (breadcrumb && stage !== "INIT") {
    breadcrumb.textContent = `SDLC Cycle &bull; ${stage}`;
  }

  // Create or close step cards based on stage
  if (stage === "SPEC") {
    currentStepCard = createStepCard("Fase 1: Especificación Formal Canónica (k-spec)", true);
    addSubStepToCard(currentStepCard, "Analizando requerimientos y matriz de 6 ACs");
    addSubStepToCard(currentStepCard, "Inyectando directivas canónicas de Karpathy v0");
  } else if (stage === "VERIFIER_RED") {
    if (currentStepCard) finishStepCard(currentStepCard, "Fase 1: Especificación Completada");
    currentStepCard = createStepCard("Fase 2: Verifier TDD - Ciclo Rojo (Fallo Inicial)", true);
    addSubStepToCard(currentStepCard, "Ejecutando suite para verificar ausencia de código");
  } else if (stage === "VERIFIER_GREEN") {
    if (currentStepCard) finishStepCard(currentStepCard, "Fase 2: Red Phase Verificada");
    currentStepCard = createStepCard("Fase 3: Verifier TDD - Ciclo Verde (Implementación)", true);
    addSubStepToCard(currentStepCard, "Compilando lógica mínima de paso y cobertura");
  } else if (stage === "COMPLETED") {
    if (currentStepCard) finishStepCard(currentStepCard, "Ciclo SDLC Finalizado con Éxito");
    currentStepCard = null;
    loadStatusAndFiles();
  }

  currentAgentBubble = null;
  currentRawContent = "";
}

function handleToken(tokenContent) {
  // If we have an active step card and token starts with step progress
  if (tokenContent.includes("🧠 Evaluando")) {
    if (!currentStepCard) currentStepCard = createStepCard("Triage & Clasificación de Intención", true);
    addSubStepToCard(currentStepCard, "Evaluando intención: QUERY vs FEATURE vs BUGFIX");
    return;
  }
  if (tokenContent.includes("📌 Especificación guardada")) {
    if (currentStepCard) addSubStepToCard(currentStepCard, tokenContent.trim());
    return;
  }

  // Conversational response bubble
  if (!currentAgentBubble) {
    const bubble = document.createElement("div");
    bubble.className = "agent-response-bubble";
    document.getElementById("chat-messages").appendChild(bubble);
    currentAgentBubble = bubble;
    currentRawContent = "";
  }

  currentRawContent += tokenContent;
  if (window.marked && typeof marked.parse === "function") {
    currentAgentBubble.innerHTML = marked.parse(currentRawContent);
  } else {
    currentAgentBubble.innerHTML = escapeHtml(currentRawContent);
  }

  const container = document.getElementById("chat-messages");
  container.scrollTop = container.scrollHeight;
}

function handleApprovalRequired(specContent, specFile) {
  if (currentStepCard) {
    finishStepCard(currentStepCard, "Fase 1: Especificación Lista (Aprobación Requerida)");
    if (specFile) addSubStepToCard(currentStepCard, `Archivo guardado: ${specFile}`);
  }

  document.getElementById("approval-bar").classList.add("active");

  // Show spec in preview or artifacts list
  loadArtifacts();

  // Scroll into view
  const approvalBar = document.getElementById("approval-bar");
  if (approvalBar) approvalBar.scrollIntoView({ behavior: "smooth" });
}

function handleTddOutput(returncode, output) {
  if (currentStepCard) {
    addSubStepToCard(currentStepCard, `Test Runner Exit Code: ${returncode}`);
  }
  const tddViewer = document.getElementById("tdd-viewer");
  if (tddViewer) {
    tddViewer.textContent += `\n[Exit Code: ${returncode}]\n${output}\n`;
  }
}

function handleCompleted(prContent) {
  appendUserOrAgentText(`🎉 **Ejecución Completada**. Todos los quality gates superados.\n\n${prContent}`, "agent");
  loadStatusAndFiles();
}

function handleError(errorMessage) {
  if (currentStepCard) {
    finishStepCard(currentStepCard, "Error en Ejecución");
    addSubStepToCard(currentStepCard, `❌ ${errorMessage}`);
  }
  appendUserOrAgentText(`❌ **Error**: ${errorMessage}`, "agent");
}

function appendUserOrAgentText(text, sender) {
  const container = document.getElementById("chat-messages");
  if (!container) return;

  if (sender === "user") {
    const userCard = document.createElement("div");
    userCard.className = "user-message-card";
    userCard.textContent = text;
    container.appendChild(userCard);
  } else {
    const bubble = document.createElement("div");
    bubble.className = "agent-response-bubble";
    if (window.marked && typeof marked.parse === "function") {
      bubble.innerHTML = marked.parse(text);
    } else {
      bubble.innerHTML = escapeHtml(text);
    }
    container.appendChild(bubble);
  }
  container.scrollTop = container.scrollHeight;
}

// ===================================================================
// Workspace Context, Files Changed & Artifacts (Right Panel)
// ===================================================================

async function loadStatusAndFiles() {
  try {
    const resStatus = await fetch("/api/status");
    if (resStatus.ok) {
      const data = await resStatus.json();
      const metaWorkspace = document.getElementById("meta-workspace");
      const metaBranch = document.getElementById("meta-branch");
      const metaStash = document.getElementById("meta-stash");
      if (metaWorkspace) metaWorkspace.textContent = data.workspace || "k-method";
      if (metaBranch) metaBranch.textContent = data.branch || "main";
      if (metaStash) metaStash.textContent = data.is_clean ? "Limpio (Clean)" : "Modificado (Dirty)";

      if (data.models) availableProviderModels = data.models;
    }
  } catch (err) {
    console.warn("Status fetch failed:", err);
  }

  // Load Git Diff & Changed files
  try {
    const resDiff = await fetch("/api/diff");
    if (resDiff.ok) {
      const diffData = await resDiff.json();
      renderChangedFiles(diffData.files || []);
    }
  } catch (err) {
    console.warn("Diff fetch failed:", err);
  }

  // Load Artifacts (specs)
  loadArtifacts();

  // Load Skills catalog
  loadSkillsCatalog();
}

function renderChangedFiles(files) {
  const listEl = document.getElementById("files-changed-list");
  const countBadge = document.getElementById("files-changed-badge");
  if (countBadge) countBadge.textContent = files.length;
  if (!listEl) return;

  listEl.innerHTML = "";
  if (files.length === 0) {
    listEl.innerHTML = '<p class="empty-note">(Working tree limpio)</p>';
    return;
  }

  files.forEach((f) => {
    const row = document.createElement("div");
    row.className = "file-row-item";
    const statusClass = f.status.includes("?") ? "added" : (f.status.includes("D") ? "deleted" : "modified");
    row.innerHTML = `
      <span class="file-dot ${statusClass}"></span>
      <div class="file-info">
        <span class="file-name">${escapeHtml(f.name)}</span>
        <span class="file-path">${escapeHtml(f.dir)}</span>
      </div>
    `;
    row.addEventListener("click", async () => {
      openPreviewModal(`Diff: ${f.name}`, `<pre style="font-family:var(--font-mono);font-size:0.8rem;">Cargando diff para ${f.path}...</pre>`);
      try {
        const res = await fetch("/api/diff");
        if (res.ok) {
          const d = await res.json();
          openPreviewModal(`Diff: ${f.name}`, `<pre style="font-family:var(--font-mono);font-size:0.82rem;white-space:pre-wrap;">${escapeHtml(d.diff || "Sin diff disponible")}</pre>`);
        }
      } catch (e) {
        console.error(e);
      }
    });
    listEl.appendChild(row);
  });
}

async function loadArtifacts() {
  try {
    const res = await fetch("/api/artifacts");
    if (!res.ok) return;
    const data = await res.json();
    const artifacts = data.artifacts || [];

    const badge = document.getElementById("artifacts-badge");
    if (badge) badge.textContent = artifacts.length;

    const listEl = document.getElementById("artifacts-list");
    if (!listEl) return;

    listEl.innerHTML = "";
    if (artifacts.length === 0) {
      listEl.innerHTML = '<p class="empty-note">Sin artefactos generados aún.</p>';
      return;
    }

    artifacts.forEach((art) => {
      const item = document.createElement("div");
      item.className = "file-row-item";
      item.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        <div class="file-info">
          <span class="file-name">${escapeHtml(art.name)}</span>
          <span class="file-path">${escapeHtml(art.slug)}</span>
        </div>
      `;
      item.addEventListener("click", async () => {
        try {
          const resp = await fetch(`/api/artifact?path=${encodeURIComponent(art.path)}`);
          if (resp.ok) {
            const body = await resp.json();
            const rendered = window.marked && typeof marked.parse === "function" ? marked.parse(body.content) : `<pre>${escapeHtml(body.content)}</pre>`;
            openPreviewModal(`Artefacto: ${art.name} (${art.slug})`, rendered);
          }
        } catch (e) {
          console.error(e);
        }
      });
      listEl.appendChild(item);
    });
  } catch (err) {
    console.warn("Artifacts fetch failed:", err);
  }
}

async function loadSkillsCatalog() {
  try {
    const res = await fetch("/api/skills");
    if (!res.ok) return;
    const data = await res.json();
    const skills = data.skills || [];

    const badge = document.getElementById("skills-badge");
    if (badge) badge.textContent = skills.length;

    const listEl = document.getElementById("skills-used-list");
    if (!listEl) return;

    listEl.innerHTML = "";
    skills.forEach((s) => {
      const row = document.createElement("div");
      row.className = "skill-row-item";
      row.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
        <div class="file-info">
          <span class="skill-name">${escapeHtml(s.name)}</span>
          <span class="skill-path">${escapeHtml(s.layer || "Karpathy v0")}</span>
        </div>
      `;
      row.addEventListener("click", () => {
        openPreviewModal(`Skill: ${s.name}`, `<h3>${escapeHtml(s.name)} (${escapeHtml(s.version || "v0")})</h3><p><strong>Capa:</strong> ${escapeHtml(s.layer)}</p><p>${escapeHtml(s.description)}</p>`);
      });
      listEl.appendChild(row);
    });
  } catch (err) {
    console.warn("Skills fetch failed:", err);
  }
}

// ===================================================================
// Preview & Settings Modals
// ===================================================================

function openPreviewModal(title, htmlContent) {
  const backdrop = document.getElementById("modal-backdrop");
  const modal = document.getElementById("preview-modal");
  const titleEl = document.getElementById("preview-modal-title");
  const bodyEl = document.getElementById("preview-modal-content");

  if (titleEl) titleEl.innerHTML = title;
  if (bodyEl) bodyEl.innerHTML = htmlContent;

  backdrop.classList.remove("hidden");
  modal.classList.remove("hidden");
  document.getElementById("settings-modal").classList.add("hidden");
}

function closeModals() {
  document.getElementById("modal-backdrop").classList.add("hidden");
  document.getElementById("settings-modal").classList.add("hidden");
  document.getElementById("preview-modal").classList.add("hidden");
}

// ===================================================================
// Event Listeners & Initialization
// ===================================================================

function initUI() {
  // Theme Toggle
  const themeBtn = document.getElementById("btn-theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "light";
      const next = current === "light" ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", next);
    });
  }

  // Model Selector Dropdown Pill
  const pillBtn = document.getElementById("btn-model-pill");
  const pickerCard = document.getElementById("model-picker-card");
  if (pillBtn && pickerCard) {
    pillBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      pickerCard.classList.toggle("hidden");
    });
    document.addEventListener("click", (e) => {
      if (!pickerCard.contains(e.target) && e.target !== pillBtn) {
        pickerCard.classList.add("hidden");
      }
    });
  }

  // Mini Tabs in Model Picker
  document.querySelectorAll(".tab-btn-mini").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn-mini").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const prov = btn.getAttribute("data-prov");
      renderPickerModelList(prov);
    });
  });

  // Custom model text input in picker
  const pickerCustomInput = document.getElementById("picker-custom-input");
  if (pickerCustomInput) {
    pickerCustomInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && pickerCustomInput.value.trim()) {
        const customVal = pickerCustomInput.value.trim();
        currentModel = customVal;
        updateModelOptions(currentProvider, customVal);
        pickerCard.classList.add("hidden");
      }
    });
  }

  // Form Submit / Send Task
  const form = document.getElementById("task-form");
  const input = document.getElementById("task-input");
  if (form && input) {
    // Auto-expand textarea
    input.addEventListener("input", () => {
      input.style.height = "auto";
      input.style.height = Math.min(input.scrollHeight, 160) + "px";
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        form.dispatchEvent(new Event("submit"));
      }
    });

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const taskText = input.value.trim();
      if (!taskText) return;

      appendUserOrAgentText(taskText, "user");
      input.value = "";
      input.style.height = "auto";

      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          action: "start",
          task: taskText,
          provider: currentProvider,
          model: currentModel,
          auto_approve: autoApprove,
        }));
      }
    });
  }

  // New Conversation Button
  const btnNewConv = document.getElementById("btn-new-conversation");
  if (btnNewConv) {
    btnNewConv.addEventListener("click", () => {
      const container = document.getElementById("chat-messages");
      if (container) {
        container.innerHTML = "";
        appendUserOrAgentText("Hola. Soy el motor de **k-method app**. Introduce una consulta o requerimiento para comenzar.", "agent");
      }
      document.getElementById("approval-bar").classList.remove("active");
      currentStepCard = null;
    });
  }

  // Restart to Update Button
  const btnRestart = document.getElementById("btn-restart-update");
  if (btnRestart) {
    btnRestart.addEventListener("click", () => {
      window.location.reload();
    });
  }

  // Approval Bar Buttons
  const btnApprove = document.getElementById("btn-approve");
  if (btnApprove) {
    btnApprove.addEventListener("click", () => {
      document.getElementById("approval-bar").classList.remove("active");
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "approval_response", approved: true }));
      }
      appendUserOrAgentText("✅ Especificación aprobada por el operador humano.", "user");
    });
  }

  const btnRevise = document.getElementById("btn-revise");
  if (btnRevise) {
    btnRevise.addEventListener("click", () => {
      document.getElementById("approval-bar").classList.remove("active");
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "approval_response", approved: false, feedback: "Revisión solicitada." }));
      }
      appendUserOrAgentText("🛑 Especificación rechazada para revisión.", "user");
    });
  }

  // Accordion Toggles
  document.querySelectorAll(".accordion-head").forEach((head) => {
    head.addEventListener("click", () => {
      const accordion = head.closest(".inspector-accordion");
      if (accordion) accordion.classList.toggle("open");
    });
  });

  // Settings Dialog Open / Close
  const btnSettings = document.getElementById("btn-settings-dialog");
  const modalBackdrop = document.getElementById("modal-backdrop");
  const settingsModal = document.getElementById("settings-modal");
  const btnCloseSettings = document.getElementById("btn-close-settings");
  const btnSaveSettings = document.getElementById("btn-save-settings");
  const btnClosePreview = document.getElementById("btn-close-preview");

  if (btnSettings && modalBackdrop && settingsModal) {
    btnSettings.addEventListener("click", () => {
      modalBackdrop.classList.remove("hidden");
      settingsModal.classList.remove("hidden");
      document.getElementById("preview-modal").classList.add("hidden");
    });
  }

  if (btnCloseSettings) btnCloseSettings.addEventListener("click", closeModals);
  if (btnClosePreview) btnClosePreview.addEventListener("click", closeModals);
  if (modalBackdrop) {
    modalBackdrop.addEventListener("click", (e) => {
      if (e.target === modalBackdrop) closeModals();
    });
  }

  if (btnSaveSettings) {
    btnSaveSettings.addEventListener("click", () => {
      const selectedRadio = document.querySelector('input[name="modal-provider"]:checked');
      if (selectedRadio) {
        currentProvider = selectedRadio.value;
        const pSelect = document.getElementById("provider-select");
        if (pSelect) pSelect.value = currentProvider;
        updateModelOptions(currentProvider);
      }
      const chkAuto = document.getElementById("modal-auto-approve");
      if (chkAuto) autoApprove = chkAuto.checked;
      closeModals();
    });
  }

  // Provider Select Change (binding for test suite contract AC-6)
  const providerSelect = document.getElementById("provider-select");
  if (providerSelect) {
    providerSelect.addEventListener("change", (e) => {
      updateModelOptions(e.target.value);
    });
  }

  // Refresh Models Button (binding for test suite contract AC-7)
  const refreshModelsBtn = document.getElementById("btn-refresh-models");
  if (refreshModelsBtn) {
    refreshModelsBtn.addEventListener("click", async () => {
      try {
        const res = await fetch("/api/models");
        if (res.ok) {
          const data = await res.json();
          if (data.models) {
            availableProviderModels = data.models;
            updateModelOptions(currentProvider, currentModel);
          }
        }
      } catch (err) {
        console.error("Refresh failed:", err);
      }
    });
  }

  // Initial welcome greeting
  appendUserOrAgentText("Hola. Soy el motor de **k-method app**. Introduce una funcionalidad, corrección o consulta para comenzar.", "agent");
}

// Bootstrap
document.addEventListener("DOMContentLoaded", () => {
  initUI();
  updateModelOptions(currentProvider);
  loadStatusAndFiles();
  connectWebSocket();
});
