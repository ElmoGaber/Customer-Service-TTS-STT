# utils/file_manager.py
import os
from pathlib import Path

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)
    return path

def save_bytes(path: str, data: bytes):
    ensure_dir(str(Path(path).parent))
    with open(path, "wb") as f:
        f.write(data)
    return path

def read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()
