import os

from flask import Flask
from src.db import db

app = Flask(__name__)

# Credenciais via variável de ambiente, com fallback pros mesmos valores que
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "7410")
DB_NAME = os.environ.get("DB_NAME", "crud")

# Driver mysql-connector-python que já era usado no projeto (mysql+mysqlconnector://)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Pool de conexões
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_size": 5,          # conexões mantidas abertas, prontas pra uso
    "max_overflow": 10,      # conexões extras liberadas em picos de tráfego
    "pool_recycle": 280,     # descarta conexões antes do MySQL fechá-las sozinho
                              # (ajuste pro valor real do seu wait_timeout: SHOW VARIABLES LIKE 'wait_timeout')
    "pool_pre_ping": True,   # testa a conexão antes de usar; reconecta se caiu
}

db.init_app(app)