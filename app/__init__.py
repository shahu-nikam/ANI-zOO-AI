import os

from flask import Flask

from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["DATASET_FOLDER"], exist_ok=True)

    from app import db
    db.init_app(app)

    from app import auth, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)

    return app
