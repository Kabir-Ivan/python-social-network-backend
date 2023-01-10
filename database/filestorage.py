from fastapi import UploadFile, File
from typing import List
from config import get_settings
import os

settings = get_settings()

if not os.path.exists(settings.STORAGE_DIR):
    os.makedirs(settings.STORAGE_DIR)


def upload_one(file: UploadFile = File(...), filename: str = 'default'):
    try:
        contents = file.file.read()
        with open(os.path.join(settings.STORAGE_DIR, filename), 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}


def upload_many(files: List[UploadFile] = File(...), filename: str = 'default'):
    for file in files:
        try:
            contents = file.file.read()
            with open(os.path.join(settings.STORAGE_DIR, filename), 'wb') as f:
                f.write(contents)
        except Exception:
            return {"message": "There was an error uploading the file(s)"}
        finally:
            file.file.close()

    return {"message": f"Successfully uploaded {[file.filename for file in files]}"}
