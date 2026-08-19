from flask_sqlalchemy import SQLAlchemy

# Instância única do SQLAlchemy, inicializada em app.py via db.init_app(app).
db = SQLAlchemy()