from flask import Flask, redirect, url_for
from flask_login import LoginManager
from models import db, User
from routes import auth_bp, main_bp
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']          = os.environ.get('SECRET_KEY', 'fintrack-secret-2025-change-me')
    app.config['SQLALCHEMY_DATABASE_URI']        = 'sqlite:///fintrack.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view     = 'auth.login'
    login_manager.login_message  = 'Faça login para continuar.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
