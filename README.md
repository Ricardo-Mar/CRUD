# CRUD de Usuários

Aplicação web para cadastro, listagem, edição e exclusão (lógica) de usuários, com back-end em Flask e banco de dados MySQL.

## Tecnologias utilizadas

- **Python 3** + **Flask** — servidor web e rotas da API REST
- **SQLAlchemy** (via **Flask-SQLAlchemy**) — ORM, sessão e pool de conexões
- **MySQL** (driver `mysql-connector-python`) — banco de dados
- **HTML5 / CSS3** — estrutura e estilo da interface (com validação nativa de formulário)
- **JavaScript (vanilla, sem frameworks)** — comunicação com a API via `fetch`

## Como executar o projeto

### Pré-requisitos
- Python 3.10 ou superior
- MySQL Server instalado e em execução

### Passo a passo

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Crie o banco a partir do dump incluído no projeto:
   ```bash
   mysql -u root -p < "Dump20260809 (1).sql"
   ```
   Isso cria o banco `crud` e a tabela `usuarios` já com a estrutura completa (incluindo `Ativo` e `Data_de_Cadastro`).

3. Confira as credenciais de conexão em `src/app.py`. Por padrão usam `localhost` / `root` / `7410` / banco `crud`; para sobrescrever sem tocar no código, defina as variáveis de ambiente `DB_HOST`, `DB_USER`, `DB_PASSWORD` e `DB_NAME`.

4. Rode a aplicação a partir da raiz do projeto:
   ```bash
   python main.py
   ```

5. Acesse **http://localhost:5000** no navegador.

## Estrutura da aplicação

```
projeto/
├── main.py                 # Ponto de entrada — inicia o servidor Flask
├── requirements.txt
└── src/
    ├── __init__.py
    ├── app.py       # Instância do Flask + config do SQLAlchemy (URI, pool)
    ├── db.py        # Instância do SQLAlchemy (db.init_app em app.py)
    ├── models.py    # Model Usuario (ORM) mapeando a tabela `usuarios`
    ├── views.py     # Rotas: página inicial + API REST de usuários
    ├── templates/
    │   └── index.html       # Interface (listagem + formulário)
    └── static/
        ├── style.css        # Estilo da interface (verde neon + roxo)
        └── script.js        # Comunicação com a API (fetch) e lógica da tela
```

### Fluxo da aplicação

`index.html` carrega `script.js`, que consome a API exposta em `views.py`:

| Ação na tela | Requisição | Rota |
|---|---|---|
| Carregar lista de usuários | `GET` | `/usuarios` |
| Cadastrar usuário | `POST` | `/usuarios` |
| Editar usuário | `PUT` | `/usuarios/<id>` |
| Excluir usuário | `DELETE` | `/usuarios/<id>` |

A exclusão é **lógica**: o registro não é removido do banco, apenas marcado com `Ativo = 0` e deixa de aparecer na listagem (`WHERE Ativo = 1` no `SELECT`).

A conexão com o banco é gerenciada pelo SQLAlchemy: um pool de conexões reaproveitadas entre requisições (configurado em `src/app.py`), em vez de abrir/fechar uma conexão nova a cada chamada. Cada rota trata erros de integridade (e-mail ou CPF já cadastrado) devolvendo HTTP 409, e demais falhas de banco devolvem HTTP 500 em vez de derrubar a aplicação.