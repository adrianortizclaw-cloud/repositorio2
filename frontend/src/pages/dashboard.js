export function createDashboardPage({ onLogout }) {
  const container = document.createElement("div");
  container.className = "page dashboard";
  container.innerHTML = `
    <div class="dashboard-header">
      <div>
        <h1>Dashboard</h1>
        <p id="dashboard-subtitle">Resumen rápido de InstagramProyect.</p>
      </div>
      <button class="logout-btn" id="dashboard-logout">Cerrar sesión</button>
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
  logoutBtn.addEventListener("click", () => onLogout());
  return container;
}
