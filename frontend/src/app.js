import "./styles/main.css";
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
    await logoutRequest();
    clearToken();
    showAuth();
  },
});

function setFeedback(message) {
  loginPage.setStatus(message);
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

function navigate(path, replace = false) {
  if (replace) {
    window.history.replaceState(null, "", path);
  } else {
    window.history.pushState(null, "", path);
  }
}

async function updateProfile(token) {
  try {
    const profile = await fetchProfile(token);
    renderDashboard(profile.username, profile.role);
  } catch (error) {
    clearToken();
    showAuth();
    setFeedback("Tu sesión expiró, vuelve a autenticarte");
  }
}

function renderDashboard(username, role) {
  root.innerHTML = "";
  root.appendChild(dashboardPage);
  setFeedback(`Autenticado como ${username} (${role})`);
  navigate(DASHBOARD_PATH, true);
}

function showAuth() {
  root.innerHTML = "";
  root.appendChild(loginPage.element);
}

function renderRoute() {
  const token = readToken();
  if (token) {
    authPage()?.classList.add("hidden");
    document.body.classList.remove("route-loading");
    if (window.location.pathname !== DASHBOARD_PATH) {
      navigate(DASHBOARD_PATH, true);
    }
    updateProfile(token);
    return;
  }
  if (window.location.pathname !== AUTH_PATH) {
    navigate(AUTH_PATH, true);
  }
  document.body.classList.remove("route-loading");
  showAuth();
}

async function handleConfirm(code, username) {
  try {
    const payload = await confirm(username, code);
    storeToken(payload.access_token);
    modal.hide();
    await updateProfile(payload.access_token);
  } catch (error) {
    setFeedback(error.message);
  }
}

function renderRoute() {
  const token = readToken();
  if (token) {
    authPage()?.classList.add("hidden");
    document.body.classList.remove("route-loading");
    if (window.location.pathname !== DASHBOARD_PATH) {
      navigate(DASHBOARD_PATH, true);
    }
    updateProfile(token);
    return;
  }
  if (window.location.pathname !== AUTH_PATH) {
    navigate(AUTH_PATH, true);
  }
  document.body.classList.remove("route-loading");
  showAuth();
}

function authPage() {
  return document.querySelector("#auth-page");
}

window.addEventListener("load", () => {
  renderRoute();
});
window.addEventListener("popstate", renderRoute);
