let autoRefresh = false;
let lastResponse = null;
let flagsCache = [];

const TYPING_IDLE_DELAY = 900;
const THEME_KEY = "theme";

const typingState = {
  timers: new Map(),
  requestVersions: new Map(),
};

const dirtyInputs = new Set();
const deletingIds = new Set();

const envSelect = document.getElementById("env");
const errorBox = document.getElementById("error");
const jsonPanel = document.getElementById("jsonPanel");
const searchInput = document.getElementById("search-box");

/* =========================================================
  THEME HELPERS
========================================================= */
function getSystemTheme() {
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

function getStoredTheme() {
  return localStorage.getItem(THEME_KEY);
}

function setStoredTheme(theme) {
  localStorage.setItem(THEME_KEY, theme);
}

function applyTheme(theme) {
  const root = document.body;

  if (theme === "dark") {
    root.classList.add("dark");
  } else {
    root.classList.remove("dark");
  }
}

function initTheme() {
  const stored = getStoredTheme();

  const theme = stored || getSystemTheme();

  applyTheme(theme);
}

function toggleTheme() {
  const isDark = document.body.classList.contains("dark");

  const newTheme = isDark ? "light" : "dark";

  applyTheme(newTheme);
  setStoredTheme(newTheme);

  updateThemeButton(newTheme);
}

function updateThemeButton(theme) {
  const btn = document.getElementById("themeToggle");

  btn.textContent = theme === "dark" ? "☀️" : "🌙";
}

// Theme Bindings
document.getElementById("themeToggle")?.addEventListener("click", toggleTheme);

window.matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", (e) => {
    const stored = getStoredTheme();
    if (stored) return; // user override wins

    applyTheme(e.matches ? "dark" : "light");
  });

initTheme();
updateThemeButton(getStoredTheme() || getSystemTheme());

/* =========================================================
  STATE HELPERS
========================================================= */

function findFlag(id) {
  return flagsCache.find(f => String(f.id) === String(id));
}

function updateFlagInCache(updated) {
  const idx = flagsCache.findIndex(f => String(f.id) === String(updated.id));
  if (idx !== -1) flagsCache[idx] = updated;
}

function removeFlagFromCache(id) {
  flagsCache = flagsCache.filter(f => String(f.id) !== String(id));
}

function getActiveEnvironment() {
  return envSelect.value;
}

/* =========================================================
  API HELPERS
========================================================= */
async function apiFetch(url, options = {}) {
  const res = await fetch(url, options);

  // Handle empty responses (204 No Content)
  const text = await res.text();

  let json = null;

  if (text) {
    try {
      json = JSON.parse(text);
    } catch {
      throw new Error("Invalid JSON response from server");
    }
  }

  if (!res.ok || (json && json.status === "error")) {
    throw new Error(json?.error?.message || "API request failed");
  }

  return json;
}

/* =========================================================
  LOAD FLAGS
========================================================= */

async function loadFlags() {
  const env = envSelect.value;
  errorBox.innerText = "";

  try {
    const json = await apiFetch(`/api/v1/flags?environment=${encodeURIComponent(env)}`);

    // Extract the data
    flagsCache = json.data;
    lastResponse = json;

    render(flagsCache);
    renderMeta();

    if (jsonPanel.style.display === "block") {
      jsonPanel.innerText = JSON.stringify(json, null, 2);
    }

  } catch (err) {
    const table = document.getElementById("flags");

    renderEmptyState(table, {
      title: "Failed to load feature flags",
      subtitle: "Something went wrong while fetching data.",
      buttonText: "Retry",
      onClick: loadFlags
    });
  }
}

/* =========================================================
  CREATE FLAG
========================================================= */

async function createFlag() {
  const name = document.getElementById("flagName").value.trim();
  const environment = document.getElementById("flagEnv").value;
  const enabled = document.getElementById("flagEnabled").value === "true";
  const description = document.getElementById("flagDescription").value.trim();
  const createBtn = document.getElementById("createBtn")

  if (!name) {
    errorBox.innerText = "Flag name is required";
    return;
  }

  createBtn.disabled = true; // Prevent double-submission
  try {
    const response = await apiFetch("/api/v1/flags", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        environment,
        enabled,
        description: description || null,
      }),
    });

    // Reset form
    document.getElementById("flagName").value = "";
    document.getElementById("flagDescription").value = "";

    closeModal();
    loadFlags();

  } catch (err) {
    errorBox.innerText = `⚠️ ${err.message}`;
  } finally {
    createBtn.disabled = false;
  }
}

/* =========================================================
  OPTIMISTIC TOGGLE
========================================================= */

async function toggleFlag(id) {
  const flag = findFlag(id);
  if (!flag) return;

  const originalState = flag.enabled;

  // Optimistic update
  flag.enabled = !originalState;
  render(flagsCache);

  try {
    const response = await apiFetch(`/api/v1/flags/${id}/toggle`, {
      method: "POST"
    });

    const updated = response.data;

    updateFlagInCache(updated);
    render(flagsCache);

  } catch(err) {
    // Revert optimistic update on failure
    flag.enabled = originalState;
    render(flagsCache);

    errorBox.innerText = `⚠️ ${err.message}`;
  }
}

/* =========================================================
  OPTIMISTIC DELETE
========================================================= */

async function deleteFlag(id) {
  // Prevent rapid duplicate deletes
  if (deletingIds.has(id)) return;

  if (!confirm("Are you sure you want to delete this flag?")) {
    return;
  }

  deletingIds.add(id);
  const snapshot = [...flagsCache];

  // Optimistic removal
  removeFlagFromCache(id);
  render(flagsCache);

  try {
    await apiFetch(`/api/v1/flags/${id}`, {
      method: "DELETE"
    });
  } catch(err) {
    // Revert UI state
    flagsCache = snapshot;
    render(flagsCache);

    errorBox.innerText = `⚠️ ${err.message}`;
  } finally {
    deletingIds.delete(id);
  }
}

/* =========================================================
  RENDER
========================================================= */

function render(data) {
  const table = document.getElementById("flags");
  table.innerHTML = "";

  // Empty State
  if (!data || data.length === 0) {
    renderEmptyState({
      title: "No feature flags found",
      subtitle: "Ready to create your first flag?",
      buttonText: "Create Feature Flag",
      onAction: () => {
        openModal();

        setTimeout(() => {
          document.getElementById("flagName")?.focus();
        }, 50);
      }
    });
    return;
  }

  // Normal Render
  data.forEach(flag => {

    const existing = document.querySelector(
      `.desc-input[data-id="${flag.id}"]`
    );

    const value =
      existing && dirtyInputs.has(String(flag.id))
        ? existing.value
        : (flag.description || "");

    const row = document.createElement("tr");

    row.innerHTML = `
      <td>
        <div><strong>${flag.name}</strong></div>
        <div class="muted">${flag.environment}</div>

        <div class="desc-wrapper">
          <input
            class="desc-input"
            data-id="${flag.id}"
            value="${flag.description || ""}"
          />

          <span class="save-indicator" data-indicator="${flag.id}"></span>
        </div>
      </td>

      <td>
        <label class="switch">
          <input
            type="checkbox"
            class="flag-toggle"
            data-id="${flag.id}"
            ${flag.enabled ? "checked" : ""}
          />
          <span class="slider">
            <span class="switch-label on">Enabled</span>
            <span class="switch-label off">Disabled</span>
          </span>
        </label>
      </td>

      <td>
        <button class="delete" data-id="${flag.id}">🗑</button>
      </td>
    `;

    table.appendChild(row);
  });

  bindHandlers();
}

function renderEmptyState(table, { title, subtitle, buttonText, onClick }) {
  table.innerHTML = "";

  const row = document.createElement("tr");

  row.innerHTML = `
    <td colspan="3" class="empty-state">
      <div class="empty-title">${title}</div>
      <div class="empty-subtitle">${subtitle}</div>

      ${buttonText ? `
        <br/>
        <button id="emptyActionBtn" class="primary">${buttonText}</button>
      ` : ""}
    </td>
  `;

  table.appendChild(row);

  if (onClick) {
    document.getElementById("emptyActionBtn")?.addEventListener("click", onClick);
  }
}

/* =========================================================
  HANDLERS
========================================================= */

function bindHandlers() {
  document.querySelectorAll(".flag-toggle").forEach(toggle => {
    toggle.addEventListener("change", () => {
      toggleFlag(toggle.dataset.id);
    });
  });

  document.querySelectorAll(".delete").forEach(btn => {
    btn.onclick = () => deleteFlag(btn.dataset.id);
  });

  document.querySelectorAll(".desc-input").forEach(input => {
    input.addEventListener("input", (e) => {
      const id = input.dataset.id;

      dirtyInputs.add(id);
      input.classList.add("typing");

      scheduleSave(id, e.target.value, input);
    });
  });

  bindSearchShortcut();
}

function bindSearchShortcut() {
  const searchInput = document.querySelector("#search-box");

  if (!searchInput) return;

  document.addEventListener(
    "keydown",
    (e) => {
      // Ignore if user is typing in inputs
      const activeTag = document.activeElement?.tagName;
      const isTypingField =
        activeTag === "INPUT" || activeTag === "TEXTAREA";

      if (isTypingField) return;

      const isCmdOrCtrl = e.metaKey || e.ctrlKey;
      const isSlash = e.key === "/";

      if (!isCmdOrCtrl || !isSlash) return;

      // Prevent browser behavior
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();

      searchInput.focus();
      searchInput.select();
    },
    true // capture phase (IMPORTANT)
  );
}

function getShortcutLabel() {
  const isMac = navigator.platform.toUpperCase().includes("MAC");
  return isMac ? "⌘ /" : "Ctrl /";
}

/* =========================================================
  SMART SAVE
========================================================= */
function scheduleSave(id, value,inputEl) {
  const flag = findFlag(id);
  if (!flag) return;

  // Always revert to the LAST SAVED value on failure
  const lastSaved = flag.savedDescription;

  // Optimistic update (do not re-render full list)
  flag.description = value;
  updateFlagInCache(flag);

  setSavingIndicator(id);

  // Cancel previous debounce timer
  if (typingState.timers.has(id)) {
    clearTimeout(typingState.timers.get(id));
  }

  // Create a unique version for this save (version token)
  const version = Date.now();
  typingState.requestVersions.set(id, version);

  const timer = setTimeout(async () => {
    try {
      const response = await apiFetch(`/api/v1/flags/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: value })
      });

      // Ignore stale responses
      const currentVersion = typingState.requestVersions.get(id);
      if (currentVersion !== version) {
        return; // A newer request exists, ignore this result
      }

      const updated = response.data;
      
      // Update both live and saved state
      flag.description = updated.description;
      flag.savedDescription = updated.description;

      updateFlagInCache(flag);
      dirtyInputs.delete(id);

      setSavedIndicator(id);

    } catch (err) {
      // Ignore stale errors
      const currentVersion = typingState.requestVersions.get(id);
      if (currentVersion !== version) {
        return;
      }

      // Revert optimistic change to last confirmed saved value
      flag.description = lastSaved;
      updateFlagInCache(flag);

      setErrorIndicator(id);
      setDescriptionValue(id, lastSaved);

    } finally {
      // Only clear if this is still the active version
      const currentVersion = typingState.requestVersions.get(id);
      if (currentVersion === version) {
        typingState.requestVersions.delete(id);
      }

      typingState.timers.delete(id);
      inputEl.classList.remove("typing");
    }

  }, TYPING_IDLE_DELAY);

  typingState.timers.set(id, timer);
}

function getIndicator(id) {
  return document.querySelector(`[data-indicator="${id}"]`);
}

function setSavingIndicator(id) {
  const el = getIndicator(id);
  if (!el) return;

  el.className = "save-indicator saving";
}

function setSavedIndicator(id) {
  const el = getIndicator(id);
  if (!el) return;

  el.className = "save-indicator saved";

  setTimeout(() => {
    el.className = "save-indicator";
  }, 1200);
}

function setErrorIndicator(id) {
  const el = getIndicator(id);
  if (!el) return;

  el.className = "save-indicator error";

  setTimeout(() => {
    el.className = "save-indicator";
  }, 1500);
}

function setDescriptionValue(id, description) {
  const descriptionInput = document.querySelector(`[data-id="${id}"]`);
  if (!descriptionInput) return;

  descriptionInput.value = description;
}

/* =========================================================
  VISUAL FEEDBACK
========================================================= */

function setSaving(input) {
  input.classList.remove("saved", "error");
  input.classList.add("saving");
}

function setSaved(input) {
  input.classList.remove("saving");
  input.classList.add("saved");

  setTimeout(() => input.classList.remove("saved"), 1000);
}

function setError(input) {
  input.classList.remove("saving");
  input.classList.add("error");
}

/* =========================================================
  SEARCH
========================================================= */

searchInput.addEventListener("input", e => {
  const q = e.target.value.toLowerCase();

  const filtered = flagsCache.filter(f =>
    f.name.toLowerCase().includes(q)
  );

  render(filtered);
});

/* =========================================================
  MODAL
========================================================= */
const modal = document.getElementById("modalOverlay");
const openModalBtn = document.getElementById("openModalBtn");
const closeModalBtn = document.getElementById("closeModalBtn");

function openModal() {
  modal.classList.remove("hidden");

  // reset state
  setTimeout(() => {
    document.getElementById("flagName").value = "";
    document.getElementById("flagDescription").value = "";

    // Auto select environment
    const envSelect = document.getElementById("flagEnv");
    envSelect.value = getActiveEnvironment();

    validateCreateForm();
    document.getElementById("flagName")?.focus();
  }, 0);
}

function closeModal() {
  modal.classList.add("hidden");

  // optional: reset form
  document.getElementById("flagName").value = "";
  document.getElementById("flagDescription").value = "";
}

// Events
openModalBtn.addEventListener("click", openModal);
closeModalBtn.addEventListener("click", closeModal);

// click outside to close
modal.addEventListener("click", (e) => {
  if (e.target === modal) closeModal();
});

// ESC key support
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModal();
});

function validateCreateForm() {
  const name = document.getElementById("flagName").value.trim();
  const btn = document.getElementById("createBtn");

  btn.disabled = name.length === 0;
}

document.getElementById("flagName")?.addEventListener("input", validateCreateForm);

/* =========================================================
  META
========================================================= */

function renderMeta() {
  document.getElementById("meta").innerText =
    "Last updated: " + new Date().toLocaleTimeString();
}

/* =========================================================
  AUTO REFRESH
========================================================= */

function toggleAutoRefresh() {
  autoRefresh = !autoRefresh;

  document.getElementById("autoBtn").innerText =
    `Auto Refresh: ${autoRefresh ? "ON" : "OFF"}`;
}

/* =========================================================
  JSON PANEL
========================================================= */

function toggleJson() {
  if (jsonPanel.style.display === "block") {
    jsonPanel.style.display = "none";
  } else {
    jsonPanel.style.display = "block";
    jsonPanel.innerText = JSON.stringify(lastResponse || {}, null, 2);
  }
}

/* =========================================================
  EVENTS
========================================================= */

document.getElementById("refreshBtn").addEventListener("click", loadFlags);
document.getElementById("autoBtn").addEventListener("click", toggleAutoRefresh);
document.getElementById("jsonBtn").addEventListener("click", toggleJson);
document
  .getElementById("createFlagForm")
  ?.addEventListener("submit", (e) => {
    e.preventDefault();
    createFlag();
  });
envSelect.addEventListener("change", loadFlags);

/* =========================================================
  POLLING
========================================================= */

setInterval(() => {
  if (autoRefresh) loadFlags();
}, 5000);

/* INIT */

document.querySelector(".search-shortcut").textContent = getShortcutLabel();
// Only show shortcut on desktop
if ("ontouchstart" in window) {
  document.querySelector(".search-shortcut").style.display = "none";
}

loadFlags();
