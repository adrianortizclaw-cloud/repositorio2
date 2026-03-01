const API_BASE = window.APP_CONFIG.apiBase;

const loginForm = document.getElementById("login-form");
const logoutBtn = document.getElementById("logout-btn");
const refreshBtn = document.getElementById("refresh-btn");
const registerForm = document.getElementById("register-form");
const statusEl = document.getElementById("status");

const STORAGE_KEY = "instagramproyect_access";

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

async function fetchProfile(token) {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("No autorizado");
  }
  return res.json();
}

async function handleLogin(event) {
  event.preventDefault();
  const form = new FormData(loginForm);
  const payload = new URLSearchParams();
  payload.append("username", form.get("username"));
  payload.append("password", form.get("password"));
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    body: payload,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    credentials: "include",
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    setStatus(`Login fallido: ${detail.detail || response.statusText}`);
    return;
  }
  const data = await response.json();
  storeToken(data.access_token);
  setStatus(`Acceso para ${data.role}`);
  await updateProfile(data.access_token);
}

async function handleLogout() {
  const response = await fetch(`${API_BASE}/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
  if (!response.ok) {
    setStatus("No se pudo cerrar sesión");
    return;
  }
  clearToken();
  setStatus("Sesión cerrada");
}

async function handleRefresh() {
  const response = await fetch(`${API_BASE}/auth/refresh`, {
    method: "POST",
    credentials: "include",
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    setStatus(`Refresh fallido: ${detail.detail || response.statusText}`);
    return;
  }
  const data = await response.json();
  storeToken(data.access_token);
  setStatus(`Token renovado (${data.role})`);
  await updateProfile(data.access_token);
}

async function handleRegister(event) {
  event.preventDefault();
  const form = new FormData(registerForm);
  const payload = {
    username: form.get("reg-username"),
    password: form.get("reg-password"),
  };
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    credentials: "include",
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    setStatus(`Registro fallido: ${detail.detail || response.statusText}`);
    return;
  }
  const data = await response.json();
  if (data.access_token) {
    storeToken(data.access_token);
    await updateProfile(data.access_token);
  }
  setStatus(`Registrado ${data.role}: usuario creado`);
}

async function updateProfile(token) {
  try {
    const profile = await fetchProfile(token);
    setStatus(`Autenticado como ${profile.username} (${profile.role})`);
  } catch (error) {
    setStatus(error.message);
  }
}

loginForm.addEventListener("submit", handleLogin);
logoutBtn.addEventListener("click", handleLogout);
refreshBtn.addEventListener("click", handleRefresh);
registerForm.addEventListener("submit", handleRegister);

const storedToken = readToken();
if (storedToken) {
  updateProfile(storedToken);
} else {
  setStatus("Necesitas autenticarte");
}
