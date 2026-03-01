export function createLoginPage({ onLogin, onRegister }) {
  const page = document.createElement("div");
  page.id = "auth-page";
  page.className = "page";
  page.innerHTML = `
    <div class="auth-wrapper">
      <div class="auth-card">
        <div class="tab-selector">
          <button data-tab="login" class="active">Login</button>
          <button data-tab="register">Register</button>
        </div>
        <div id="login-pane" class="form-pane active">
          <label>Correo</label>
          <input type="email" name="login-username" required value="client@example.com" />
          <label>Contraseña</label>
          <input type="password" name="login-password" required value="secret" />
          <button class="primary" id="login-btn">Submit</button>
        </div>
        <div id="register-pane" class="form-pane">
          <label>Correo</label>
          <input type="email" name="register-username" required placeholder="nuevo@instagramproyect.com" />
          <label>Contraseña</label>
          <input type="password" name="register-password" required placeholder="Contraseña segura" />
          <label>Confirmar contraseña</label>
          <input type="password" name="register-confirm" required placeholder="Repite la contraseña" />
          <button class="primary" id="register-btn" disabled>Submit</button>
        </div>
        <p class="feedback" id="status"></p>
      </div>
    </div>
  `;

  const loginPane = page.querySelector("#login-pane");
  const registerPane = page.querySelector("#register-pane");
  const buttons = page.querySelectorAll(".tab-selector button");
  const statusEl = page.querySelector(".feedback#status");
  const registerBtn = page.querySelector("#register-btn");
  const registerPassword = registerPane.querySelector("input[name=register-password]");
  const registerConfirm = registerPane.querySelector("input[name=register-confirm]");

  buttons.forEach((button) =>
    button.addEventListener("click", () => {
      buttons.forEach((btn) => btn.classList.toggle("active", btn === button));
      loginPane.classList.toggle("active", button.dataset.tab === "login");
      registerPane.classList.toggle("active", button.dataset.tab === "register");
    })
  );

  const loginButton = loginPane.querySelector("#login-btn");
  loginButton.addEventListener("click", () => {
    const username = loginPane.querySelector("input[name=login-username]").value.trim();
    const password = loginPane.querySelector("input[name=login-password]").value;
    onLogin(username, password).catch((err) => setStatus(err.message));
  });

  const checkRegister = () => {
    const matches = registerPassword.value && registerPassword.value === registerConfirm.value;
    registerBtn.disabled = !matches;
  };

  registerPassword.addEventListener("input", checkRegister);
  registerConfirm.addEventListener("input", checkRegister);

  registerBtn.addEventListener("click", () => {
    const username = registerPane.querySelector("input[name=register-username]").value.trim();
    const password = registerPassword.value;
    onRegister(username, password).catch((err) => setStatus(err.message));
  });

  function setStatus(message) {
    statusEl.textContent = message;
  }

  return { element: page, setStatus };
}
