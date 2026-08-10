# CRUD de Usuários

Aplicação web para cadastro, listagem, edição e exclusão (lógica) de usuários, com back-end em Flask e banco de dados MySQL.

## Tecnologias utilizadas

- **Python 3** + **Flask** — servidor web e rotas da API REST
- **MySQL** (via `mysql-connector-python`) — banco de dados
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

3. Confira as credenciais de conexão em `src/db.py` (host, usuário, senha) e ajuste se necessário para bater com o seu MySQL local.

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
    ├── app.py               # Instância do Flask
    ├── db.py                # Função de conexão com o MySQL
    ├── views.py             # Rotas: página inicial + API REST de usuários
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

Cada rota que acessa o banco usa `try / except / finally`, garantindo que a conexão seja sempre fechada e que tentativas de cadastrar um e-mail ou CPF já existente devolvam uma mensagem de erro (HTTP 409) em vez de derrubar a aplicação.
