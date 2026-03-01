const API_BASE = window.APP_CONFIG?.apiBase || "http://localhost:8000";

const defaultFetch = async (url, options = {}) => {
  const response = await fetch(url, options);
  const json = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(json.detail || response.statusText || "Error de autenticación");
  }
  return json;
};

export const login = (username, password) =>
  defaultFetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username, password }),
    credentials: "include",
  });

export const register = (username, password) =>
  defaultFetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
    credentials: "include",
  });

export const confirm = (username, code) =>
  defaultFetch(`${API_BASE}/auth/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, code, purpose: "register" }),
    credentials: "include",
  });

export const fetchProfile = (token) =>
  defaultFetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    credentials: "include",
  });

export const logout = () =>
  fetch(`${API_BASE}/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
