import mysql.connector

from src.app import app
from src.db import conexao
from flask import render_template, request, jsonify

# Define os dados obrigatórios para o cadastro/edição de usuário
CAMPOS_OBRIGATORIOS = ["nome", "email", "cpf", "telefone", "data_nascimento"]

# Colunas devolvidas em todas consultas de usuário
SELECT_USUARIO = (
    "SELECT ID, Nome, Email, CPF, Telefone, Data_de_Nascimento, Data_de_Cadastro, Ativo "
    "FROM usuarios"
)

# Valida se o JSON tem todos os campos obrigatórios
def json_valido(dados):
    if not dados:
        return False
    return all(str(dados.get(campo, "")).strip() for campo in CAMPOS_OBRIGATORIOS)


def formatar_usuario(linha):
    """Converte uma linha (tupla) da tabela usuarios num formato seguro
    pra JSON, formatando as datas em texto aqui no Python (nunca no SQL,
    pra não misturar o %Y/%m/%d do MySQL com o %s de parâmetro do driver)."""
    id_, nome, email, cpf, telefone, nascimento, cadastro, ativo = linha
    return [
        id_,
        nome,
        email,
        cpf,
        telefone,
        nascimento.strftime("%Y-%m-%d") if nascimento else None,
        cadastro.strftime("%Y-%m-%d %H:%M:%S") if cadastro else None,
        ativo,
    ]


# ------------------------------ ROTAS ------------------------------

# Página principal (home)
@app.route("/")
def home():
    return render_template("index.html")


# Create (com reativação automática de usuário excluído)
@app.route("/usuarios", methods=["POST"])
def criarUsuario():
    dados = request.get_json(silent=True)
    if not json_valido(dados):
        return jsonify({"erro": "Preencha todos os campos obrigatórios."}), 400

    conector = conexao()
    cursor = conector.cursor()
    try:
        # Verifica se já existe algum cadastro (ativo ou não) com esse e-mail ou CPF
        cursor.execute(
            "SELECT ID, Ativo FROM usuarios WHERE Email = %s OR CPF = %s",
            (dados["email"], dados["cpf"]),
        )
        existentes = cursor.fetchall()

        if existentes:
            # Mais de um cadastro batendo (e-mail e CPF pertencem a pessoas
            # diferentes) ou o cadastro encontrado já está ativo
            if len(existentes) > 1 or existentes[0][1] == 1:
                return jsonify({"erro": "Já existe um usuário cadastrado com esse e-mail ou CPF."}), 409

            # Único cadastro encontrado e está inativo -> reativa em vez de duplicar
            usuario_id = existentes[0][0]
            query = ("UPDATE usuarios "
                     "SET Nome = %s, Email = %s, CPF = %s, Telefone = %s, Data_de_Nascimento = %s, Ativo = 1 "
                     "WHERE ID = %s")
            cursor.execute(query, (
                dados["nome"], dados["email"], dados["cpf"],
                dados["telefone"], dados["data_nascimento"], usuario_id,
            ))
            conector.commit()
            return jsonify({"mensagem": "Usuário reativado com sucesso", "id": usuario_id}), 200

        # Não existe nenhum cadastro -> cria um novo
        query = "INSERT INTO usuarios (Nome, Email, CPF, Telefone, Data_de_Nascimento) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (
            dados["nome"],
            dados["email"],
            dados["cpf"],
            dados["telefone"],
            dados["data_nascimento"],
        ))
        conector.commit()
        novo_id = cursor.lastrowid
        return jsonify({"mensagem": "Usuário criado com sucesso", "id": novo_id}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"erro": "Já existe um usuário cadastrado com esse e-mail ou CPF."}), 409
    except mysql.connector.Error:
        return jsonify({"erro": "Não foi possível salvar o usuário. Tente novamente."}), 500
    finally:
        cursor.close()
        conector.close()


# Read (lista todos, ou filtra por nome com ?nome=...)
@app.route("/usuarios", methods=["GET"])
def listarUsuarios():
    nome_busca = request.args.get("nome", "").strip()

    conector = conexao()
    cursor = conector.cursor()
    try:
        query = SELECT_USUARIO + " WHERE Ativo = 1"
        parametros = ()
        if nome_busca:
            query += " AND Nome LIKE %s"
            parametros = (f"%{nome_busca}%",)
        query += " ORDER BY ID DESC"

        cursor.execute(query, parametros)
        resultado = cursor.fetchall()
        return jsonify([formatar_usuario(linha) for linha in resultado])
    except mysql.connector.Error:
        return jsonify({"erro": "Não foi possível carregar os usuários."}), 500
    finally:
        cursor.close()
        conector.close()


# Read (consulta um único usuário por ID)
@app.route("/usuarios/<int:usuario_id>", methods=["GET"])
def buscarUsuarioPorId(usuario_id):
    conector = conexao()
    cursor = conector.cursor()
    try:
        cursor.execute(SELECT_USUARIO + " WHERE ID = %s AND Ativo = 1", (usuario_id,))
        resultado = cursor.fetchone()
        if not resultado:
            return jsonify({"erro": "Usuário não encontrado."}), 404
        return jsonify(formatar_usuario(resultado))
    except mysql.connector.Error:
        return jsonify({"erro": "Não foi possível buscar o usuário."}), 500
    finally:
        cursor.close()
        conector.close()


# Update
@app.route("/usuarios/<int:usuario_id>", methods=["PUT"])
def atualizarUsuario(usuario_id):
    dados = request.get_json(silent=True)
    if not json_valido(dados):
        return jsonify({"erro": "Preencha todos os campos obrigatórios."}), 400

    conector = conexao()
    cursor = conector.cursor()
    try:
        query = ("UPDATE usuarios "
                 "SET Nome = %s, Email = %s, CPF = %s, Telefone = %s, Data_de_Nascimento = %s "
                 "WHERE ID = %s AND Ativo = 1")
        cursor.execute(query, (
            dados["nome"],
            dados["email"],
            dados["cpf"],
            dados["telefone"],
            dados["data_nascimento"],
            usuario_id,
        ))
        conector.commit()
        linhas_atualizadas = cursor.rowcount

        if linhas_atualizadas == 0:
            return jsonify({"erro": "Usuário não encontrado."}), 404
        return jsonify({"mensagem": "Usuário atualizado"})
    except mysql.connector.IntegrityError:
        return jsonify({"erro": "Já existe um usuário cadastrado com esse e-mail ou CPF."}), 409
    except mysql.connector.Error:
        return jsonify({"erro": "Não foi possível atualizar o usuário. Tente novamente."}), 500
    finally:
        cursor.close()
        conector.close()


# Delete lógico
@app.route("/usuarios/<int:usuario_id>", methods=["DELETE"])
def deletarUsuario(usuario_id):
    conector = conexao()
    cursor = conector.cursor()
    try:
        cursor.execute("UPDATE usuarios SET Ativo = 0 WHERE ID = %s AND Ativo = 1", (usuario_id,))
        conector.commit()
        linhas_atualizadas = cursor.rowcount
        if linhas_atualizadas == 0:
            return jsonify({"erro": "Usuário não encontrado."}), 404
        return jsonify({"mensagem": "Usuário excluído"})
    except mysql.connector.Error:
        return jsonify({"erro": "Não foi possível excluir o usuário. Tente novamente."}), 500
    finally:
        cursor.close()
        conector.close()