const API_BASE = window.APP_CONFIG.apiBase;

const authPage = document.getElementById("auth-page");
const dashboardPage = document.getElementById("dashboard-page");
const loginPane = document.getElementById("login-pane");
const registerPane = document.getElementById("register-pane");
const loginTabButtons = document.querySelectorAll(".tab-selector button");
const feedbackEl = document.getElementById("status");
const dashboardSubtitle = document.getElementById("dashboard-subtitle");

const loginBtn = document.getElementById("login-btn");
const registerBtn = document.getElementById("register-btn");
const dashboardLogout = document.getElementById("dashboard-logout");
const modal = document.getElementById("code-modal");
const modalMessage = document.getElementById("modal-message");
const modalPreview = document.getElementById("modal-preview");
const modalCodeInput = document.getElementById("modal-code");
const modalConfirm = document.getElementById("modal-confirm");
const modalClose = document.getElementById("modal-close");

const loginUsername = loginPane.querySelector("input[name=\"login-username\"]");
const loginPassword = loginPane.querySelector("input[name=\"login-password\"]");
const registerUsername = registerPane.querySelector("input[name=\"register-username\"]");
const registerPassword = registerPane.querySelector("input[name=\"register-password\"]");
const registerConfirm = registerPane.querySelector("input[name=\"register-confirm\"]");

const STORAGE_KEY = "instagramproyect_access";
let pendingUser = null;
let pendingPurpose = null;

function setFeedback(text) {
  feedbackEl.textContent = text;
}

function storeToken(token) {
  localStorage.setItem(STORAGE_KEY, token);
}

function readToken() {
  return localStorage.getItem(STORAGE_KEY);
}

function clearToken() {
  localStorage.removeItem(STORAGE_KEY);
}

function showTab(tab) {
  loginPane.classList.toggle("active", tab === "login");
  registerPane.classList.toggle("active", tab === "register");
  loginTabButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tab);
  });
}

function showModal(username, purpose, preview) {
  pendingUser = username;
  pendingPurpose = purpose;
  modalMessage.textContent = "Se te ha enviado un código a tu email, escríbelo aquí.";
  modalPreview.textContent = preview ? `Código (test): ${preview}` : "";
  modalCodeInput.value = "";
  modal.classList.remove("hidden");
  modalCodeInput.focus();
}

function hideModal() {
  modal.classList.add("hidden");
  modalPreview.textContent = "";
}

function showDashboard(username, role) {
  authPage.classList.add("hidden");
  dashboardPage.classList.add("active");
  dashboardPage.classList.remove("hidden");
  dashboardSubtitle.textContent = `Último acceso: ${new Date().toLocaleString()}`;
  setFeedback(`Autenticado como ${username} (${role})`);
  if (window.location.pathname !== DASHBOARD_PATH) {
    navigate(DASHBOARD_PATH);
  }
}

function showAuth() {
  dashboardPage.classList.remove("active");
  dashboardPage.classList.add("hidden");
  authPage.classList.remove("hidden");
  showTab("login");
  if (window.location.pathname !== AUTH_PATH) {
    navigate(AUTH_PATH);
  }
}

function updateRegisterButtonState() {
  const valid = registerUsername.value.trim() && registerPassword.value && registerPassword.value === registerConfirm.value;
  registerBtn.disabled = !valid;
}

async function requestJson(url, options) {
  const response = await fetch(url, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || "Error de autenticación");
  }
  return payload;
}

async function handleLogin(event) {
  event.preventDefault();
  try {
    const payload = await requestJson(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        username: loginUsername.value.trim(),
        password: loginPassword.value.trim(),
      }),
      credentials: "include",
    });
    storeToken(payload.access_token);
    await updateProfile(payload.access_token);
  } catch (error) {
    setFeedback(error.message);
  }
}

async function handleRegister(event) {
  event.preventDefault();
  try {
    const payload = await requestJson(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: registerUsername.value.trim(),
        password: registerPassword.value.trim(),
      }),
      credentials: "include",
    });
    showModal(payload.username, payload.purpose, payload.code_preview);
  } catch (error) {
    setFeedback(error.message);
  }
}

async function handleConfirm() {
  const code = modalCodeInput.value.trim();
  if (!code || !pendingUser) {
    setFeedback("Introduce el código recibido por correo");
    return;
  }
  try {
    const payload = await requestJson(`${API_BASE}/auth/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: pendingUser, code, purpose: pendingPurpose }),
      credentials: "include",
    });
    storeToken(payload.access_token);
    hideModal();
    await updateProfile(payload.access_token);
  } catch (error) {
    setFeedback(error.message);
  }
}

async function handleLogout() {
  await fetch(`${API_BASE}/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
  clearToken();
  hideModal();
  showAuth();
  setFeedback("Sesión cerrada");
}

async function updateProfile(token) {
  try {
    const response = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
      credentials: "include",
    });
    if (!response.ok) {
      throw new Error("Token inválido");
    }
    const payload = await response.json();
    showDashboard(payload.username, payload.role);
  } catch (error) {
    clearToken();
    showAuth();
    setFeedback("Tu sesión expiró, vuelve a autenticarte");
  }
}

loginBtn.addEventListener("click", handleLogin);
registerBtn.addEventListener("click", handleRegister);
modalConfirm.addEventListener("click", handleConfirm);
modalClose.addEventListener("click", () => {
  hideModal();
});
dashboardLogout.addEventListener("click", handleLogout);

loginTabButtons.forEach((button) => {
  button.addEventListener("click", () => showTab(button.dataset.tab));
});

[registerPassword, registerConfirm, registerUsername].forEach((input) => {
  input.addEventListener("input", updateRegisterButtonState);
});

const AUTH_PATH = "/login";
const DASHBOARD_PATH = "/dashboard";

function navigate(path, replace = false) {
  if (replace) {
    window.history.replaceState(null, "", path);
  } else {
    window.history.pushState(null, "", path);
  }
}

function renderRoute() {
  const token = readToken();
  if (token) {
    if (window.location.pathname !== DASHBOARD_PATH) {
      navigate(DASHBOARD_PATH, true);
    }
    updateProfile(token);
    return;
  }
  if (window.location.pathname !== AUTH_PATH) {
    navigate(AUTH_PATH, true);
  }
  showAuth();
}

window.addEventListener("load", async () => {
  updateRegisterButtonState();
  renderRoute();
});

window.addEventListener("popstate", () => {
  renderRoute();
});
