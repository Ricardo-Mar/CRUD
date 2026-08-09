const API_URL = "/usuarios";

const form = document.getElementById("user-form");
const grid = document.getElementById("user-grid");
const emptyState = document.getElementById("empty-state");
const formTitle = document.getElementById("form-title");
const submitBtn = document.getElementById("submit-btn");
const cancelBtn = document.getElementById("cancel-btn");
const idOriginalInput = document.getElementById("id-original");

let usuarioParaExcluir = null;

// ---------- Toast ----------
function toast(msg, type = "ok") {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.className = "show " + type;
  setTimeout(() => { el.className = ""; }, 2800);
}

// ---------- Validação ----------
function setFieldError(id, hasError) {
  document.getElementById(id).closest(".field").classList.toggle("has-error", hasError);
}

function validarFormulario() {
  let valido = true;
  const nome = document.getElementById("nome").value.trim();
  const email = document.getElementById("email").value.trim();
  const cpf = document.getElementById("cpf").value.trim();
  const telefone = document.getElementById("telefone").value.trim();
  const nascimento = document.getElementById("data_nascimento").value.trim();

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const cpfRegex = /^\d{3}\.\d{3}\.\d{3}-\d{2}$/;

  setFieldError("nome", !nome); if (!nome) valido = false;
  setFieldError("email", !emailRegex.test(email)); if (!emailRegex.test(email)) valido = false;
  setFieldError("cpf", !cpfRegex.test(cpf)); if (!cpfRegex.test(cpf)) valido = false;
  setFieldError("telefone", !telefone); if (!telefone) valido = false;
  setFieldError("data_nascimento", !nascimento); if (!nascimento) valido = false;

  return valido;
}

// ---------- Renderização da lista ----------
function renderUsuarios(lista) {
  grid.innerHTML = "";

  if (!lista || lista.length === 0) {
    emptyState.style.display = "block";
    return;
  }
  emptyState.style.display = "none";

  lista.forEach(u => {
    const card = document.createElement("div");
    card.className = "user-card";
    card.innerHTML = `
      <div class="u-top">
        <p class="u-nome">${escapeHtml(u.Nome)}</p>
        <span class="u-id">#${u.ID}</span>
      </div>
      <dl>
        <div><dt>E-mail</dt><dd>${escapeHtml(u.Email)}</dd></div>
        <div><dt>CPF</dt><dd>${escapeHtml(u.CPF)}</dd></div>
        <div><dt>Telefone</dt><dd>${escapeHtml(u.Telefone)}</dd></div>
        <div><dt>Nasc.</dt><dd>${escapeHtml(String(u.Data_de_Nascimento).slice(0,10))}</dd></div>
      </dl>
      <div class="u-actions">
        <button class="btn-edit">Editar</button>
        <button class="btn-delete">Excluir</button>
      </div>
    `;
    card.querySelector(".btn-edit").addEventListener("click", () => entrarModoEdicao(u));
    card.querySelector(".btn-delete").addEventListener("click", () => abrirModalExclusao(u));
    grid.appendChild(card);
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

// ---------- Carregar usuários (READ) ----------
async function carregarUsuarios() {
  try {
    const resp = await fetch(API_URL);
    if (!resp.ok) throw new Error("Falha ao buscar usuários");
    const dados = await resp.json();
    renderUsuarios(dados);
  } catch (e) {
    toast("Não foi possível carregar os usuários.", "err");
  }
}

// ---------- Modo edição ----------
function entrarModoEdicao(usuario) {
  document.getElementById("nome").value = usuario.Nome;
  document.getElementById("email").value = usuario.Email;
  document.getElementById("cpf").value = usuario.CPF;
  document.getElementById("telefone").value = usuario.Telefone;
  document.getElementById("data_nascimento").value = String(usuario.Data_de_Nascimento).slice(0, 10);
  idOriginalInput.value = usuario.ID;

  formTitle.textContent = "Editar usuário";
  submitBtn.textContent = "Salvar alterações";
  cancelBtn.style.display = "inline-block";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function sairModoEdicao() {
  form.reset();
  idOriginalInput.value = "";
  formTitle.textContent = "Novo usuário";
  submitBtn.textContent = "Cadastrar";
  cancelBtn.style.display = "none";
  ["nome", "email", "cpf", "telefone", "data_nascimento"].forEach(id => setFieldError(id, false));
}

cancelBtn.addEventListener("click", sairModoEdicao);

// ---------- Criar / Atualizar (CREATE / UPDATE) ----------
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!validarFormulario()) {
    toast("Confira os campos destacados.", "err");
    return;
  }

  const payload = {
    nome: document.getElementById("nome").value.trim(),
    email: document.getElementById("email").value.trim(),
    cpf: document.getElementById("cpf").value.trim(),
    telefone: document.getElementById("telefone").value.trim(),
    data_nascimento: document.getElementById("data_nascimento").value.trim(),
  };

  const editando = !!idOriginalInput.value;
  const url = editando ? `${API_URL}/${idOriginalInput.value}` : API_URL;
  const method = editando ? "PUT" : "POST";

  try {
    const resp = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!resp.ok) throw new Error("Erro na requisição");

    toast(editando ? "Usuário atualizado com sucesso." : "Usuário cadastrado com sucesso.");
    sairModoEdicao();
    carregarUsuarios();
  } catch (err) {
    toast("Não foi possível salvar o usuário.", "err");
  }
});

// ---------- Exclusão (DELETE) ----------
const modalOverlay = document.getElementById("modal-overlay");
const modalUserName = document.getElementById("modal-user-name");

function abrirModalExclusao(usuario) {
  usuarioParaExcluir = usuario;
  modalUserName.textContent = usuario.Nome;
  modalOverlay.classList.add("show");
}

function fecharModal() {
  modalOverlay.classList.remove("show");
  usuarioParaExcluir = null;
}

document.getElementById("modal-cancel").addEventListener("click", fecharModal);
modalOverlay.addEventListener("click", (e) => { if (e.target === modalOverlay) fecharModal(); });

document.getElementById("modal-confirm").addEventListener("click", async () => {
  if (!usuarioParaExcluir) return;
  try {
    const resp = await fetch(`${API_URL}/${usuarioParaExcluir.ID}`, { method: "DELETE" });
    if (!resp.ok) throw new Error("Erro ao excluir");
    toast("Usuário excluído.");
    if (idOriginalInput.value == usuarioParaExcluir.ID) sairModoEdicao();
    carregarUsuarios();
  } catch (err) {
    toast("Não foi possível excluir o usuário.", "err");
  } finally {
    fecharModal();
  }
});

// ---------- Início ----------
carregarUsuarios();