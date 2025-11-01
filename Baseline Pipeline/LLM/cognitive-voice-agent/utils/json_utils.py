# utils/json_utils.py
import json
from pathlib import Path

def save_json(path: str, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return path

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
