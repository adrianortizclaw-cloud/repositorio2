const API_BASE = process.env.API_BASE || "http://localhost:8000";

async function checkHealth() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed (${response.status})`);
  }
  return response.json();
}

async function login(username, password) {
  const payload = new URLSearchParams();
  payload.append("username", username);
  payload.append("password", password);

  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    body: payload,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(`Login failed: ${detail.detail || response.statusText}`);
  }
  return response.json();
}

async function register(username, password) {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(`Register failed: ${detail.detail || response.statusText}`);
  }
  return response.json();
}

async function confirm(username, code, purpose = "login") {
  const response = await fetch(`${API_BASE}/auth/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, code, purpose }),
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(`Confirm failed: ${detail.detail || response.statusText}`);
  }
  return response.json();
}

async function profile(token) {
  const response = await fetch(`${API_BASE}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error(`Profile check failed (${response.status})`);
  }
  return response.json();
}

async function run() {
  console.log(`API base: ${API_BASE}`);
  const health = await checkHealth();
  console.log("Health OK", health);

  const loginRes = await login("client@example.com", "secret");
  console.log("Login code sent", loginRes.code_preview);

  const confirmRes = await confirm(loginRes.username, loginRes.code_preview, loginRes.purpose);
  console.log("Confirmed, tokens", confirmRes);

  const profileData = await profile(confirmRes.access_token);
  console.log("Profile", profileData);

  const adminLogin = await login("admin@example.com", "secret");
  const adminConfirm = await confirm(adminLogin.username, adminLogin.code_preview, adminLogin.purpose);
  const adminStatus = await fetch(`${API_BASE}/auth/admin`, {
    headers: { Authorization: `Bearer ${adminConfirm.access_token}` },
  });
  if (!adminStatus.ok) {
    throw new Error(`Admin route failed (${adminStatus.status})`);
  }
  console.log("Admin route OK");

  const registerEmail = `smoke+${Date.now()}@example.com`;
  const registerRes = await register(registerEmail, "pass1234");
  const registerConfirm = await confirm(registerRes.username, registerRes.code_preview, registerRes.purpose);
  console.log("Register + confirm OK", registerConfirm.access_token);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});