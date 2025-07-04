# interface/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap # <--- Utiliser cet import
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap() # <--- Initialiser ici

login_manager.login_view = 'main.login'
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
login_manager.login_message_category = "info"

def create_app():
    app = Flask(__name__)

    database_url = os.getenv('DATABASE_URL')
    secret_key = os.getenv('SECRET_KEY')

    if not database_url:
        raise ValueError("ERREUR : 'DATABASE_URL' non définie. Vérifiez .env !")
    if not secret_key:
        print("ATTENTION : SECRET_KEY non définie.")
        secret_key = 'default-unsafe-key'

    app.config['SECRET_KEY'] = secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app) # <--- Lier à l'app

    with app.app_context():
        from api_config.api_script.models import User, SessionLocal

        @login_manager.user_loader
        def load_user(user_id):
            db_session = SessionLocal()
            user = db_session.query(User).get(int(user_id))
            db_session.close()
            return user

        from .routes import main as main_blueprint
        app.register_blueprint(main_blueprint)

    return app