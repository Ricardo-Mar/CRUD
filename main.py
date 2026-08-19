import src.views  # noqa: F401 — importa só pelo efeito colateral de registrar as rotas
from src.app import app

if __name__ == "__main__":
    app.run(debug=True)