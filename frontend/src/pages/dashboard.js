export function createDashboardPage({ onLogout, onAddInstagram }) {
  const container = document.createElement("div");
  container.className = "page dashboard";
  container.innerHTML = `
    <div class="dashboard-header">
      <div>
        <h1>Dashboard</h1>
        <p id="dashboard-subtitle">Resumen rápido de InstagramProyect.</p>
      </div>
      <div class="dashboard-actions">
        <button class="instagram-btn" id="instagram-add">Add Instagram account</button>
        <button class="logout-btn" id="dashboard-logout">Cerrar sesión</button>
      </div>
    </div>
    <div class="instagram-summary">
      <p id="instagram-username">Instagram: no conectado</p>
      <p id="instagram-media">Publicaciones: 0</p>
    </div>
    <div class="metrics">
      <div class="metric-card">
        <h3>Campañas activas</h3>
        <p>8 activos sincronizados.</p>
      </div>
      <div class="metric-card">
        <h3>Alertas</h3>
        <p>1 alarma crítica (métricas fuera de rango).</p>
      </div>
      <div class="metric-card">
        <h3>Códigos pendientes</h3>
        <p>Generamos códigos automáticos tras cada inicio de sesión.</p>
      </div>
    </div>
  `;
  const logoutBtn = container.querySelector("#dashboard-logout");
  const addBtn = container.querySelector("#instagram-add");
  const usernameEl = container.querySelector("#instagram-username");
  const mediaEl = container.querySelector("#instagram-media");
  logoutBtn.addEventListener("click", () => onLogout());
  addBtn.addEventListener("click", () => onAddInstagram());

  function setInstagramInfo({ username, mediaCount }) {
    usernameEl.textContent = username ? `Instagram: ${username}` : "Instagram: no conectado";
    mediaEl.textContent = `Publicaciones: ${mediaCount ?? 0}`;
  }

  return { element: container, setInstagramInfo };
}
