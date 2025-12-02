import os
from werkzeug.utils import secure_filename
from flask import current_app, request
from config import Config
from time import time
from docx import Document

ALLOWED_EXT = {"pdf","docx"}


def get_data_root():
    return os.environ.get("DATA_ROOT", Config.DATA_ROOT)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


def save_onboarding_file(file, employee_id):
    base = get_data_root()
    folder = os.path.join(base,"uploads","onboarding", str(employee_id))
    os.makedirs(folder, exist_ok=True)
    timestamp = str(int(time.time()))
    filename=f"{timestamp}_{secure_filename(file.filename)}"
    path = os.path.join(folder, filename)
    file.save(path)
    return path, filename, file.mimetype
