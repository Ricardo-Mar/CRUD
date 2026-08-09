from ftplib import error_proto
from idlelib import query

from mysql import connector

from src.app import app
from src.db import conexao
from flask import render_template, request, jsonify

#Define os dados obrigatórios para o banco de dados
NotNull = ["nome", "email", "cpf", "telefone", "data_nascimento"]

#Valida se o json tem todos os dados obrigatórios
def json_valido(dados):
    if not(dados):
        return False
    return all (str (dados.get(campo, "")).strip() for campo in NotNull)



# ------------------------------ ROTAS ------------------------------

#Página principal (home)
@app.route("/")
def home():
    return render_template("index.html")


#Create
@app.route("/usuario", methods=["POST"])
def criarUsuario():
    dados = request.get_json(silent=True)
    if not json_valido(dados):
        return jsonify({"Preencha todos os campos obrigatórios ": NotNull}), 400

    connector = conexao()
    cursor = connector.cursor()
    query = "INSERT INTO usuarios (Nome, Email, Cpf, Telefone, Data_de_Nascimento) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (
        dados ["nome"],
        dados ["email"],
        dados ["cpf"],
        dados ["telefone"],
        dados ["data_nascimento"]
    ))
    connector.commit()
    novo_id = cursor.lastrowid
    cursor.close()
    connector.close()
    return jsonify({"Sucesso": "Usuário criado com sucesso", "id": novo_id}), 201