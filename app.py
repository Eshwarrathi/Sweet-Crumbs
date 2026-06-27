from pathlib import Path

from flask import Flask, render_template

from config import Config
from extensions import db, login_manager
from helpers import format_money


def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from blueprints.auth import bp as auth_bp
    from blueprints.shop import bp as shop_bp
    from blueprints.cart import bp as cart_bp
    from blueprints.orders import bp as orders_bp
    from blueprints.reviews import bp as reviews_bp
    from blueprints.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(admin_bp)

    app.jinja_env.filters["money"] = format_money

    @app.context_processor
    def inject_globals():
        from models import Category

        return {
            "STORE_NAME": app.config["STORE_NAME"],
            "CURRENCY_SYMBOL": app.config["CURRENCY_SYMBOL"],
            "nav_categories": Category.query.order_by(Category.name).limit(8).all(),
        }

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("Database tables created.")

    with app.app_context():
        import time
        for _ in range(3):
            try:
                db.create_all()
                break
            except Exception as e:
                app.logger.warning("Database init attempt failed: %s", e)
                time.sleep(1)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
