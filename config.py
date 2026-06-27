import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production-please")

    _database_url = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'shop.db'}"
    )
    if _database_url.startswith("postgres://"):
        _database_url = _database_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

    STORE_NAME = os.environ.get("STORE_NAME", "Sweet Crumbs")
    CURRENCY = os.environ.get("CURRENCY", "PKR")
    CURRENCY_SYMBOL = os.environ.get("CURRENCY_SYMBOL", "Rs.")
    ITEMS_PER_PAGE = 12

    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@sweetcrumbs.com")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
