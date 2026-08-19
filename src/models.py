from src.db import db


# Mapeia a tabela `usuarios` existente no banco.

class Usuario(db.Model):

    __tablename__ = "usuarios"

    ID = db.Column(db.Integer, primary_key=True)
    Nome = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), nullable=False)
    CPF = db.Column(db.String(20), nullable=False)
    Telefone = db.Column(db.String(30), nullable=False)
    Data_de_Nascimento = db.Column(db.Date, nullable=False)
    Data_de_Cadastro = db.Column(db.DateTime)
    Ativo = db.Column(db.Integer)

    def to_array(self):
        """
        Mesmo formato de lista que o front-end espera em script.js,
        Objeto COL: [ID, Nome, Email, CPF, Telefone, Nascimento, Cadastro, Ativo]
        """
        return [
            self.ID,
            self.Nome,
            self.Email,
            self.CPF,
            self.Telefone,
            self.Data_de_Nascimento.strftime("%Y-%m-%d") if self.Data_de_Nascimento else None,
            self.Data_de_Cadastro.strftime("%Y-%m-%d %H:%M:%S") if self.Data_de_Cadastro else None,
            self.Ativo,
        ]