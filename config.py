import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Change this in production (set as an environment variable instead).
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # SQLite database file (auto-created on first run).
    DATABASE = os.path.join(BASE_DIR, "instance", "app.db")

    # Where user-uploaded images are stored.
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")

    # Where labelled "unknown animal" images are stored (used to grow the
    # training dataset), organized as dataset/animal/<animal_name>/*.jpg
    DATASET_FOLDER = os.path.join(BASE_DIR, "dataset", "animal")

    # Trained model files.
    MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "ani_model.keras")
    CLASS_PATH = os.path.join(BASE_DIR, "ml_models", "ani_classes.pkl")

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    CONFIDENCE_THRESHOLD = 50

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max upload size
