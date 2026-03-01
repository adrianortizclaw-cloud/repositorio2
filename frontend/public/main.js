const API_BASE = window.APP_CONFIG.apiBase;

const authPage = document.getElementById("auth-page");
const dashboardPage = document.getElementById("dashboard-page");
const loginPane = document.getElementById("login-pane");
const registerPane = document.getElementById("register-pane");
const confirmSection = document.getElementById("confirm-section");
const confirmMessage = document.getElementById("confirm-message");
const confirmPreview = document.getElementById("confirm-preview");
const loginTabButtons = document.querySelectorAll(".tab-selector button");
const statusEl = document.getElementById("status");
const dashboardSubtitle = document.getElementById("dashboard-subtitle");

const loginBtn = document.getElementById("login-btn");
const registerBtn = document.getElementById("register-btn");
const confirmBtn = document.getElementById("confirm-btn");
const dashboardLogout = document.getElementById("dashboard-logout");

const loginUsername = loginPane.querySelector("input[name=\"login-username\"]");
const loginPassword = loginPane.querySelector("input[name=\"login-password\"]");
const registerUsername = registerPane.querySelector("input[name=\"register-username\"]");
const registerPassword = registerPane.querySelector("input[name=\"register-password\"]");
const confirmCodeInput = document.getElementById("confirm-code");

const STORAGE_KEY = "instagramproyect_access";
let pendingUser = null;
let pendingPurpose = null;

function setStatus(text) {
  statusEl.textContent = text;
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

function showConfirmSection(username, purpose, preview) {
  pendingUser = username;
  pendingPurpose = purpose;
  confirmSection.classList.remove("hidden");
  confirmCodeInput.value = "";
  confirmMessage.textContent = `Código enviado a ${username}.`;
  confirmPreview.textContent = preview ? `Código (testing): ${preview}` : "";
}

function hideConfirmSection() {
  confirmSection.classList.add("hidden");
  confirmMessage.textContent = "";
  confirmPreview.textContent = "";
  pendingUser = null;
  pendingPurpose = null;
}

async function updateProfile(token) {
  try {
    const profile = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
      credentials: "include",
    });
    if (profile.ok) {
      const payload = await profile.json();
      setStatus(`Autenticado como ${payload.username} (${payload.role})`);
      dashboardSubtitle.textContent = `Último acceso: ${new Date().toLocaleString()}`;
      showDashboard(payload.username, payload.role);
    } else {
      throw new Error("Token inválido");
    }
  } catch (error) {
    clearToken();
    showAuth();
    setStatus("Tu sesión expiró, vuelve a autenticarte");
  }
}

function showDashboard(username, role) {
  authPage.classList.add("hidden");
  dashboardPage.classList.add("active");
  dashboardPage.classList.remove("hidden");
  setStatus(`Autenticado como ${username} (${role})`);
}

function showAuth() {
  dashboardPage.classList.remove("active");
  dashboardPage.classList.add("hidden");
  authPage.classList.remove("hidden");
  showTab("login");
}

async function requestCode(endpoint, payload, options = {}) {
  const response = await fetch(`${API_BASE}/auth/${endpoint}`, {
    method: "POST",
    headers: options.headers || {},
    body: options.body,
    credentials: "include",
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Error de autenticación");
  }
  return data;
}

async function handleLogin(event) {
  event.preventDefault();
  try {
    const data = await requestCode("login", {
      body: new URLSearchParams({
        username: loginUsername.value.trim(),
        password: loginPassword.value.trim(),
      }),
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    setStatus(`Código enviado a ${data.username}`);
    showConfirmSection(data.username, data.purpose, data.code_preview);
  } catch (error) {
    setStatus(error.message);
  }
}

async function handleRegister(event) {
  event.preventDefault();
  try {
    const payload = {
      username: registerUsername.value.trim(),
      password: registerPassword.value.trim(),
    };
    const data = await requestCode("register", {
      body: JSON.stringify(payload),
      headers: { "Content-Type": "application/json" },
    });
    setStatus(`Código enviado a ${data.username}`);
    showConfirmSection(data.username, data.purpose, data.code_preview);
  } catch (error) {
    setStatus(error.message);
  }
}

async function handleConfirm(event) {
  event.preventDefault();
  if (!pendingUser) {
    setStatus("Inicia primero login o registro");
    return;
  }
  const code = confirmCodeInput.value.trim();
  if (!code) {
    setStatus("Introduce el código de verificación");
    return;
  }
  try {
    const response = await fetch(`${API_BASE}/auth/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: pendingUser, code, purpose: pendingPurpose }),
      credentials: "include",
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Código incorrecto");
    }
    storeToken(payload.access_token);
    hideConfirmSection();
    await updateProfile(payload.access_token);
  } catch (error) {
    setStatus(error.message);
  }
}

async function handleLogout() {
  await fetch(`${API_BASE}/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
  clearToken();
  hideConfirmSection();
  showAuth();
  setStatus("Sesión cerrada");
}

loginBtn.addEventListener("click", handleLogin);
registerBtn.addEventListener("click", handleRegister);
confirmBtn.addEventListener("click", handleConfirm);
dashboardLogout.addEventListener("click", handleLogout);

loginTabButtons.forEach((button) => {
  button.addEventListener("click", () => showTab(button.dataset.tab));
});

window.addEventListener("load", async () => {
  const token = readToken();
  if (token) {
    await updateProfile(token);
  }
});
