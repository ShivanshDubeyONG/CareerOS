import os
import shutil
import uuid

from fastapi import UploadFile

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
UPLOAD_FOLDER = "uploads"


def is_allowed_file(filename: str) -> bool:
    return filename.lower().endswith(tuple(ALLOWED_EXTENSIONS))


def generate_unique_filename(filename: str) -> str:
    extension = os.path.splitext(filename)[1]
    return f"{uuid.uuid4()}{extension}"


async def save_file(file: UploadFile, filename: str) -> None:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

def get_file_path(filename: str) -> str:
    return os.path.join(UPLOAD_FOLDER, filename)