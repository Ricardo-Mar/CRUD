from contextlib import contextmanager

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.app import app
from src.db import db
from src.models import Usuario
from flask import render_template, request, jsonify


# Define os dados obrigatórios para o cadastro/edição de usuário
CAMPOS_OBRIGATORIOS = ["nome", "email", "cpf", "telefone", "data_nascimento"]


# Valida se o JSON tem todos os campos obrigatórios
def json_valido(dados):
    if not dados:
        return False
    return all(str(dados.get(campo, "")).strip() for campo in CAMPOS_OBRIGATORIOS)


# --------------------------- TRANSAÇÃO COM O BANCO ---------------------------

@contextmanager
def db_transaction():
    """
    Equivalente ao antigo db_cursor(commit=True): garante commit automático
    ao final do bloco e rollback em caso de erro.
    """
    try:
        yield db.session
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


# ------------------------------ ROTAS ------------------------------

# Página principal (home)
@app.route("/")
def home():
    return render_template("index.html")


from datetime import datetime
import re

# Create
@app.route("/usuarios", methods=["POST"])
def criarUsuario():
    dados = request.get_json(silent=True)
    if not json_valido(dados):
        return jsonify({"erro": "Preencha todos os campos obrigatórios."}), 400

    import re
    # Limpa pontuação do CPF
    cpf_limpo = re.sub(r"\D", "", dados.get("cpf", ""))

    try:
        data_nasc = datetime.strptime(dados["data_nascimento"], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return jsonify({"erro": "Data de nascimento inválida."}), 400

    try:
        # Busca usuário existente por E-mail ou CPF limpo
        existente = Usuario.query.filter(
            or_(Usuario.Email == dados["email"], Usuario.CPF == cpf_limpo)
        ).first()

        if existente:
            if existente.Ativo == 1:
                return jsonify({"erro": "Já existe um usuário cadastrado com esse e-mail ou CPF."}), 409

            # Reativa usuário se estava inativo
            existente.Nome = dados["nome"]
            existente.Email = dados["email"]
            existente.CPF = cpf_limpo
            existente.Telefone = dados["telefone"]
            existente.Data_de_Nascimento = data_nasc
            existente.Ativo = 1

            db.session.commit()
            return jsonify({"mensagem": "Usuário reativado com sucesso", "id": existente.ID}), 200

        # Cria um novo usuário.
        novo = Usuario(
            Nome=dados["nome"],
            Email=dados["email"],
            CPF=cpf_limpo,
            Telefone=dados["telefone"],
            Data_de_Nascimento=data_nasc,
            Ativo=1,
            Data_de_Cadastro=datetime.now()
        )
        db.session.add(novo)
        db.session.commit()

        return jsonify({"mensagem": "Usuário criado com sucesso", "id": novo.ID}), 201

    # Imprime erro no terminal
    except IntegrityError as e:
        db.session.rollback()
        print("Erro de Integridade:", e)
        return jsonify({"erro": "Já existe um usuário cadastrado com esse e-mail ou CPF."}), 409

    except SQLAlchemyError as e:
        db.session.rollback()
        print("Erro do SQLAlchemy:", e)
        return jsonify({"erro": "Não foi possível salvar o usuário. Tente novamente."}), 500


# Read (lista todos, ou filtra por nome com ?nome=...)
@app.route("/usuarios", methods=["GET"])
def listarUsuarios():
    nome_busca = request.args.get("nome", "").strip()

    query = Usuario.query.filter(Usuario.Ativo == 1)
    if nome_busca:
        query = query.filter(Usuario.Nome.like(f"%{nome_busca}%"))
    query = query.order_by(Usuario.ID.desc())

    try:
        resultado = query.all()
        return jsonify([usuario.to_array() for usuario in resultado])
    except SQLAlchemyError:
        return jsonify({"erro": "Não foi possível carregar os usuários."}), 500


# Read (consulta um único usuário por ID)
@app.route("/usuarios/<int:usuario_id>", methods=["GET"])
def buscarUsuarioPorId(usuario_id):
    try:
        usuario = Usuario.query.filter_by(ID=usuario_id, Ativo=1).first()
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado."}), 404
        return jsonify(usuario.to_array())
    except SQLAlchemyError:
        return jsonify({"erro": "Não foi possível buscar o usuário."}), 500


# Update
@app.route("/usuarios/<int:usuario_id>", methods=["PUT"])
def atualizarUsuario(usuario_id):
    dados = request.get_json(silent=True)
    if not json_valido(dados):
        return jsonify({"erro": "Preencha todos os campos obrigatórios."}), 400

    try:
        with db_transaction():
            linhas_atualizadas = Usuario.query.filter_by(ID=usuario_id, Ativo=1).update({
                "Nome": dados["nome"],
                "Email": dados["email"],
                "CPF": dados["cpf"],
                "Telefone": dados["telefone"],
                "Data_de_Nascimento": dados["data_nascimento"],
            })

        if linhas_atualizadas == 0:
            return jsonify({"erro": "Usuário não encontrado."}), 404
        return jsonify({"mensagem": "Usuário atualizado"})
    except IntegrityError:
        return jsonify({"erro": "Já existe um usuário cadastrado com esse e-mail ou CPF."}), 409
    except SQLAlchemyError:
        return jsonify({"erro": "Não foi possível atualizar o usuário. Tente novamente."}), 500


# Delete lógico
@app.route("/usuarios/<int:usuario_id>", methods=["DELETE"])
def deletarUsuario(usuario_id):
    try:
        with db_transaction():
            linhas_atualizadas = Usuario.query.filter_by(ID=usuario_id, Ativo=1).update({"Ativo": 0})

        if linhas_atualizadas == 0:
            return jsonify({"erro": "Usuário não encontrado."}), 404
        return jsonify({"mensagem": "Usuário excluído"})
    except SQLAlchemyError:
        return jsonify({"erro": "Não foi possível excluir o usuário. Tente novamente."}), 500
