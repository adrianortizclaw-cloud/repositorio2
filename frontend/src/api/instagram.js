const API_BASE = window.APP_CONFIG?.apiBase || "http://localhost:8000";

const defaultFetch = async (url, options = {}) => {
  const response = await fetch(url, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || response.statusText || "Instagram request failed");
  }
  return payload;
};

const sessionFetch = (url, sessionId) =>
  defaultFetch(url, {
    headers: { "X-Session-Id": sessionId },
  });

export const getInstagramLoginUrl = () =>
  defaultFetch(`${API_BASE}/api/instagram/login-url`);

export const getInstagramSession = (sessionId) =>
  sessionFetch(`${API_BASE}/api/instagram/session`, sessionId);

export const getInstagramMe = (sessionId) =>
  sessionFetch(`${API_BASE}/api/instagram/me`, sessionId);

export const getInstagramMedia = (sessionId) =>
  sessionFetch(`${API_BASE}/api/instagram/media`, sessionId);
