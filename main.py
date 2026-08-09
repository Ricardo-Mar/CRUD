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
criar = f'INSERT INTO usuarios (Nome, Email, CPF, Telefone, Data_de_Nascimento) VALUES ("{nome}", "{email}", "{cpf}", "{telefone}", "{data_de_nascimento}")'
cursor.execute(criar)
conector.commit() #edita o banco de dados


#READ
ler = 'SELECT * FROM usuarios'
cursor.execute(ler)
resultado = cursor.fetchall() #ler o banco de dados
print(resultado)


#UPDATE
nome2 = "joao"
atualizar = f'UPDATE usuarios SET Nome = "{nome2}" WHERE Nome = "{nome}"'
cursor.execute(atualizar) #atualiza o valor do banco de dados
conector.commit()

#READ
ler = 'SELECT * FROM usuarios'
cursor.execute(ler)
resultado = cursor.fetchall() #ler o banco de dados
print(resultado)


#DELETE
deletar = f'DELETE FROM usuarios WHERE Nome = "{nome2}";'
cursor.execute(deletar)
conector.commit()

#READ
ler = 'SELECT * FROM usuarios'
cursor.execute(ler)
resultado = cursor.fetchall() #ler o banco de dados
print(resultado)


cursor.close()
conector.close()