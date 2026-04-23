"""Flask application factory for the Wedding Management Dashboard."""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()


def create_app() -> Flask:
    """Flask application factory: initializes app, database, auth, and blueprints."""
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration from environment variables
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///wedding.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["BASE_URL"] = os.environ.get("BASE_URL", "http://localhost:5050")

    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize Flask extensions (database, authentication, migrations, security)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"
    migrate.init_app(app, db)
    csrf.init_app(app)

    from app.models import User

    # Load user from session cookie for authentication
    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(user_id)

    # Import and register all route blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.guests import guests_bp
    from app.routes.checkin import checkin_bp
    from app.routes.invitation import invitation_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(guests_bp)
    app.register_blueprint(checkin_bp)
    app.register_blueprint(invitation_bp)

    return app
