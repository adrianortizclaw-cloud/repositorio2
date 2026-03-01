export function createModal({ onConfirm, onCancel }) {
  const modal = document.createElement("div");
  modal.className = "code-modal hidden";
  modal.innerHTML = `
    <div class="code-modal__card">
      <p id="modal-message">Se te ha enviado un código a tu correo.</p>
      <input type="text" id="modal-code" maxlength="6" placeholder="Introduce el código" />
      <p class="status" id="modal-preview"></p>
      <button class="primary" id="modal-confirm">Confirmar código</button>
      <button class="code-modal__close" id="modal-close">Cancelar</button>
    </div>
  `;
  const confirmBtn = modal.querySelector("#modal-confirm");
  const closeBtn = modal.querySelector("#modal-close");
  const codeInput = modal.querySelector("#modal-code");
  const previewEl = modal.querySelector("#modal-preview");
  const messageEl = modal.querySelector("#modal-message");

  confirmBtn.addEventListener("click", () => {
    const code = codeInput.value.trim();
    if (!code) {
      return;
    }
    onConfirm(code, modal.dataset.currentUser);
  });
  closeBtn.addEventListener("click", () => onCancel());

  function show({ username, preview }) {
    modal.dataset.currentUser = username;
    modal.classList.remove("hidden");
    codeInput.value = "";
    messageEl.textContent = `Se te ha enviado un código a ${username}.`;
    previewEl.textContent = preview ? `Código (test): ${preview}` : "";
    codeInput.focus();
  }

  function hide() {
    modal.classList.add("hidden");
    previewEl.textContent = "";
  }

  return { modal, show, hide };
}
