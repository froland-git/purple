from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from config import config # from sys.path/config.py import dictionary config


bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
login_manager.session_protection = 'strong' # strong means to check clients IP address
login_manager.login_view = 'auth.login' # blueprint name = auth, route = login

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app) # init_app is not a staticmethod from config.py

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint # from ./main
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint # from ./auth
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
