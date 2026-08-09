import mysql.connector

def conexao():
    """Abre uma nova conexão com o banco.
    Deve ser chamada uma vez a cada requisição (nunca reaproveitada
    entre chamadas diferentes) e sempre fechada no fim do uso."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="7410",
        database="crud",
    )