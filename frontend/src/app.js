import { createLoginPage } from "./pages/login.js";
import { createDashboardPage } from "./pages/dashboard.js";
import { createModal } from "./components/modal.js";
import { login, register, confirm, fetchProfile, logout as logoutRequest } from "./api/auth.js";

const AUTH_PATH = "/login";
const DASHBOARD_PATH = "/dashboard";
const STORAGE_KEY = "instagramproyect_access";

const root = document.getElementById("root");
const modal = createModal({
  onConfirm: async (code, username) => handleConfirm(code, username),
  onCancel: () => modal.hide(),
});
document.body.appendChild(modal.modal);

const loginPage = createLoginPage({
  onLogin: async (username, password) => {
    const payload = await login(username, password);
    storeToken(payload.access_token);
    await updateProfile(payload.access_token);
  },
  onRegister: async (username, password) => {
    const payload = await register(username, password);
    setFeedback(`Código enviado a ${payload.username}`);
    modal.show({ username: payload.username, preview: payload.code_preview });
  },
});

const dashboardPage = createDashboardPage({
  onLogout: async () => {
    try {
      await logoutRequest();
    } catch (_) {
      // ignoramos errores de logout remoto
    }
    clearToken();
    dashboardPage.classList.remove("active");
    showAuth();
  },
});

function setFeedback(msg) {
  loginPage.setStatus(msg);
}

function storeToken(t) {
  localStorage.setItem(STORAGE_KEY, t);
}

function readToken() {
  return localStorage.getItem(STORAGE_KEY);
}

function clearToken() {
  localStorage.removeItem(STORAGE_KEY);
}

function navigate(path, replace = false) {
  replace ? window.history.replaceState(null, "", path) : window.history.pushState(null, "", path);
}

function showAuth() {
  root.innerHTML = "";
  root.appendChild(loginPage.element);
  navigate(AUTH_PATH, true);
}

function renderDashboard(username, role) {
  root.innerHTML = "";
  dashboardPage.classList.add("active");
  dashboardPage.querySelector("#dashboard-subtitle").textContent = `Último acceso: ${new Date().toLocaleString()}`;
  root.appendChild(dashboardPage);
  navigate(DASHBOARD_PATH, true);
}

async function updateProfile(token) {
  try {
    const profile = await fetchProfile(token);
    renderDashboard(profile.username, profile.role);
  } catch {
    clearToken();
    showAuth();
    setFeedback("Tu sesión expiró, vuelve a autenticarte");
  }
}

async function handleConfirm(code, username) {
  try {
    const payload = await confirm(username, code);
    storeToken(payload.access_token);
    modal.hide();
    await updateProfile(payload.access_token);
  } catch (e) {
    modal.modal.querySelector("#modal-preview").textContent = e.message;
  }
}

function renderRoute() {
  const token = readToken();
  if (token) {
    root.innerHTML = "";
    dashboardPage.classList.add("active");
    root.appendChild(dashboardPage);
    document.body.classList.remove("route-loading");
    navigate(DASHBOARD_PATH, true);
    updateProfile(token);
    return;
  }
  navigate(AUTH_PATH, true);
  document.body.classList.remove("route-loading");
  showAuth();
}

window.addEventListener("load", renderRoute);
window.addEventListener("popstate", renderRoute);
