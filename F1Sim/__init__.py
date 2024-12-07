from flask import Flask

def create_app():
    app = Flask(__name__)

    # Registrazione dei blueprint
    from .lineup import lineup_blueprint  # Importa il blueprint
    app.register_blueprint(lineup_blueprint)

    # Altre inizializzazioni (es: database, estensioni)
    # init_db(app)  # Esempio: inizializzazione database

    return app
