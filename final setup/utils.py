import os
import logging

def setup_logger():
    """تهيئة اللوجر"""
    logger = logging.getLogger("AI_Voice_Assistant")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("system.log", encoding='utf-8')
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def ensure_dir(path):
    """تأكد إن المسار موجود"""
    if not os.path.exists(path):
        os.makedirs(path)

def get_model_path(model_type):
    """ترجع المسار المناسب للموديل"""
    base = "models"
    mapping = {
        "llm": f"{base}/llm",
        "stt": f"{base}/stt",
        "tts": f"{base}/tts",
        "eq_ar_en": f"{base}/equalizer_ar_en",
        "eq_saudi": f"{base}/equalizer_saudi"
    }
    return mapping.get(model_type, None)
