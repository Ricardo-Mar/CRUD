const API_URL = "/usuarios";

const form = document.getElementById("user-form");
const grid = document.getElementById("user-grid");
const emptyState = document.getElementById("empty-state");
const formTitle = document.getElementById("form-title");
const submitBtn = document.getElementById("submit-btn");
const cancelBtn = document.getElementById("cancel-btn");
const idOriginalInput = document.getElementById("id-original");
const buscaInput = document.getElementById("busca-input");
const buscaBtn = document.getElementById("busca-btn");

// A API devolve cada usuário como array (sem dictionary=True no cursor),
// na mesma ordem das colunas escolhidas no SELECT_USUARIO (views.py):
// [ID, Nome, Email, CPF, Telefone, Data_de_Nascimento, Data_de_Cadastro, Ativo]
const COL = { ID: 0, NOME: 1, EMAIL: 2, CPF: 3, TELEFONE: 4, NASCIMENTO: 5 };

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
        <p class="u-nome">${escapeHtml(u[COL.NOME])}</p>
        <span class="u-id">#${u[COL.ID]}</span>
      </div>
      <dl>
        <div><dt>E-mail</dt><dd>${escapeHtml(u[COL.EMAIL])}</dd></div>
        <div><dt>CPF</dt><dd>${escapeHtml(u[COL.CPF])}</dd></div>
        <div><dt>Telefone</dt><dd>${escapeHtml(u[COL.TELEFONE])}</dd></div>
        <div><dt>Nasc.</dt><dd>${escapeHtml(u[COL.NASCIMENTO])}</dd></div>
      </dl>
      <div class="u-actions">
        <button type="button" class="btn-edit">Editar</button>
        <button type="button" class="btn-delete">Excluir</button>
      </div>
    `;
    card.querySelector(".btn-edit").addEventListener("click", () => entrarModoEdicao(u));
    card.querySelector(".btn-delete").addEventListener("click", () => excluirUsuario(u));
    grid.appendChild(card);
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

// ---------- Carregar / consultar usuários (READ) ----------
// busca vazia -> lista todos; só números -> consulta por ID; texto -> busca por nome
async function carregarUsuarios(busca = "") {
  if (/^\d+$/.test(busca)) {
    const resp = await fetch(`${API_URL}/${busca}`);
    const usuario = resp.ok ? await resp.json() : null;
    renderUsuarios(usuario ? [usuario] : []);
    return;
  }

  const url = busca ? `${API_URL}?nome=${encodeURIComponent(busca)}` : API_URL;
  const resp = await fetch(url);
  const dados = await resp.json();
  renderUsuarios(dados);
}

buscaBtn.addEventListener("click", () => carregarUsuarios(buscaInput.value.trim()));
buscaInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") carregarUsuarios(buscaInput.value.trim());
});

// ---------- Modo edição ----------
function entrarModoEdicao(u) {
  document.getElementById("nome").value = u[COL.NOME];
  document.getElementById("email").value = u[COL.EMAIL];
  document.getElementById("cpf").value = u[COL.CPF];
  document.getElementById("telefone").value = u[COL.TELEFONE];
  document.getElementById("data_nascimento").value = u[COL.NASCIMENTO];
  idOriginalInput.value = u[COL.ID];

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
}

cancelBtn.addEventListener("click", sairModoEdicao);

// ---------- Criar / Atualizar (CREATE / UPDATE) ----------
form.addEventListener("submit", async (e) => {
  e.preventDefault();

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

  const resp = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!resp.ok) {
    const erro = await resp.json().catch(() => null);
    alert(erro?.erro || "Não foi possível salvar o usuário.");
    return;
  }

  sairModoEdicao();
  carregarUsuarios(buscaInput.value.trim());
});

// ---------- Exclusão (DELETE) ----------
async function excluirUsuario(u) {
  const confirmar = confirm(`Tem certeza que deseja excluir ${u[COL.NOME]}?`);
  if (!confirmar) return;

  const resp = await fetch(`${API_URL}/${u[COL.ID]}`, { method: "DELETE" });
  if (!resp.ok) {
    const erro = await resp.json().catch(() => null);
    alert(erro?.erro || "Não foi possível excluir o usuário.");
    return;
  }

  if (idOriginalInput.value == u[COL.ID]) sairModoEdicao();
  carregarUsuarios(buscaInput.value.trim());
}

// ---------- Início ----------
carregarUsuarios();