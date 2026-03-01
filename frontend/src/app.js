import { createLoginPage } from "./pages/login.js";
import { createDashboardPage } from "./pages/dashboard.js";
import { createModal } from "./components/modal.js";
import { login, register, confirm, fetchProfile, logout as logoutRequest } from "./api/auth.js";
import { getInstagramLoginUrl, getInstagramSession, getInstagramMe, getInstagramMedia } from "./api/instagram.js";

const AUTH_PATH = "/login";
const DASHBOARD_PATH = "/dashboard";
const STORAGE_KEY = "instagramproyect_access";
const INSTAGRAM_SESSION_KEY = "instagram_session";

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
  onInstagramLogin: handleInstagramLogin,
});

const dashboardPage = createDashboardPage({
  onLogout: async () => {
    try {
      await logoutRequest();
    } catch (_) {
      // ignoramos errores de logout remoto
    }
    clearToken();
    dashboardPage.element.classList.remove("active");
    showAuth();
  },
  onAddInstagram: handleInstagramLogin,
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

function storeInstagramSession(id) {
  localStorage.setItem(INSTAGRAM_SESSION_KEY, id);
}

function readInstagramSession() {
  return localStorage.getItem(INSTAGRAM_SESSION_KEY);
}

function clearInstagramSession() {
  localStorage.removeItem(INSTAGRAM_SESSION_KEY);
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
  dashboardPage.element.classList.add("active");
  dashboardPage.element.querySelector("#dashboard-subtitle").textContent = `Último acceso: ${new Date().toLocaleString()}`;
  root.appendChild(dashboardPage.element);
  navigate(DASHBOARD_PATH, true);
  refreshInstagramSummary(readInstagramSession());
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

async function handleInstagramLogin() {
  try {
    const payload = await getInstagramLoginUrl();
    window.location.href = payload.url;
  } catch (error) {
    setFeedback(error.message);
  }
}

async function hydrateInstagramSession() {
  const params = new URLSearchParams(window.location.search);
  let sessionId = params.get("session");
  if (sessionId) {
    storeInstagramSession(sessionId);
    params.delete("session");
    const path = window.location.pathname;
    const suffix = params.toString() ? `?${params.toString()}` : "";
    window.history.replaceState({}, "", `${path}${suffix}`);
  }
  sessionId = sessionId || readInstagramSession();
  if (!sessionId) {
    return null;
  }
  try {
    await getInstagramSession(sessionId);
    storeInstagramSession(sessionId);
    setFeedback("Instagram conectada");
    await refreshInstagramSummary(sessionId);
    return sessionId;
  } catch (error) {
    clearInstagramSession();
    setFeedback("No se pudo recuperar la sesión de Instagram");
    return null;
  }
}

async function refreshInstagramSummary(sessionId) {
  if (!sessionId || !dashboardPage.setInstagramInfo) {
    return;
  }
  try {
    const info = await getInstagramMe(sessionId);
    const media = await getInstagramMedia(sessionId);
    const mediaCount = Array.isArray(media?.data) ? media.data.length : 0;
    dashboardPage.setInstagramInfo({ username: info.username || info.ig_user_id || "Instagram", mediaCount });
  } catch (_) {
    dashboardPage.setInstagramInfo({ username: null, mediaCount: 0 });
  }
}

async function renderRoute() {
  await hydrateInstagramSession();
  const token = readToken();
  if (token) {
    root.innerHTML = "";
    dashboardPage.element.classList.add("active");
    root.appendChild(dashboardPage.element);
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
