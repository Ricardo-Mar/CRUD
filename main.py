from idlelib import query
from venv import create  #CRIANDO O CRUD

import mysql.connector

conector = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="7410",
    database="crud",
)
cursor = conector.cursor()

#CREATE
nome = "maria"
email = "mariazinha@gmail.com"
cpf = "123.123.123-08"
telefone = "+55 79 91111-1111"
data_de_nascimento = "2005/01/01"
criar = 'INSERT INTO usuarios (nome, email, cpf, telefone, data_de_nascimento) VALUES (%s, %s, %s, %s, %s)'
cursor.execute(criar, (nome, email, cpf, telefone, data_de_nascimento))
conector.commit() #edita o banco de dados


#READ
ler = 'SELECT * FROM usuarios'
cursor.execute(ler)
resultado = cursor.fetchall() #ler o banco de dados
print(resultado)


#UPDATE
nome2 = "joao"
cursor.execute(f'UPDATE usuarios SET Nome = %s  WHERE Nome = %s', (nome2, nome)) #atualiza o valor do banco de dados
conector.commit()

#READ
ler = 'SELECT * FROM usuarios'
cursor.execute(ler)
resultado = cursor.fetchall() #ler o banco de dados
print(resultado)


#DELETE
cursor.execute("DELETE FROM usuarios WHERE Nome = %s", (nome2,))
conector.commit()

#READ
ler = 'SELECT * FROM usuarios'
cursor.execute(ler)
resultado = cursor.fetchall() #ler o banco de dados
print(resultado)


cursor.close()
conector.close()