import os
import re
import uuid
from functools import wraps
from pathlib import Path

from flask import abort, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    text = re.sub(r"[-\s]+", "-", text)
    return text or uuid.uuid4().hex[:8]


def unique_slug(model, base_text: str) -> str:
    base = slugify(base_text)
    candidate = base
    i = 2
    while model.query.filter_by(slug=candidate).first() is not None:
        candidate = f"{base}-{i}"
        i += 1
    return candidate


def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def save_upload(file_storage) -> str | None:
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return None
    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_folder: Path = current_app.config["UPLOAD_FOLDER"]
    upload_folder.mkdir(parents=True, exist_ok=True)
    file_storage.save(upload_folder / filename)
    return filename


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def format_money(amount: float) -> str:
    symbol = current_app.config.get("CURRENCY_SYMBOL", "$")
    return f"{symbol} {amount:,.2f}"
