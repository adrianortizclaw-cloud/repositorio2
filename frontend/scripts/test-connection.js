const API_BASE = process.env.API_BASE || "http://localhost:8000";

async function checkHealth() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed (${response.status})`);
  }
  const json = await response.json();
  console.log(`Health: ${JSON.stringify(json)}`);
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

async function profile(accessToken) {
  const response = await fetch(`${API_BASE}/auth/me`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  if (!response.ok) {
    throw new Error(`Profile check failed (${response.status})`);
  }
  return response.json();
}

async function adminPing(accessToken) {
  const response = await fetch(`${API_BASE}/auth/admin`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  return response;
}

async function run() {
  console.log(`API base: ${API_BASE}`);
  await checkHealth();
  console.log("Health OK");

  const clientLogin = await login("client@example.com", "secret");
  console.log("Client login OK", clientLogin);

  const clientProfile = await profile(clientLogin.access_token);
  console.log("Client profile", clientProfile);

  const adminLogin = await login("admin@example.com", "secret");
  console.log("Admin login OK", adminLogin);

  const adminResponse = await adminPing(adminLogin.access_token);
  if (!adminResponse.ok) {
    throw new Error(`Admin ping failed (${adminResponse.status})`);
  }
  console.log("Admin route OK");
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
