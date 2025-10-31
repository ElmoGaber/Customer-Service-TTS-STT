import os
import soundfile as sf
import logging
from src.utils.logger_config import get_logger

# تأكد أن مجلد logs موجود
os.makedirs("logs", exist_ok=True)

# أنشئ لوج خاص بـ io_utils
logger = get_logger("io_utils", "logs/io_utils.log")


def load_audio_file(file_path: str):
    """
    Load an audio file (WAV/FLAC/MP3) and return (audio_data, sample_rate).
    Logs and handles errors gracefully.
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        audio_data, sample_rate = sf.read(file_path)
        logger.info(f"Loaded audio file '{file_path}' | Duration: {len(audio_data)/sample_rate:.2f}s | SR={sample_rate}")
        return audio_data, sample_rate

    except Exception as e:
        logger.exception(f"Error loading audio file: {e}")
        raise e
