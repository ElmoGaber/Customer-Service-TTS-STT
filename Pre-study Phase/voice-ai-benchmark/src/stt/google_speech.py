from pathlib import Path
from .placeholder_base import BaseSTT
from src.utils.logger_config import get_logger
import time

logger = get_logger('google_speech')


class GoogleSpeechSTT(BaseSTT):
    def __init__(self, config: dict = None):
        super().__init__(config or {})

    def transcribe(self, audio_path: Path) -> str:
        logger.info(f"Starting local placeholder transcription for {audio_path}")
        # Placeholder behavior: simulate latency and return dummy transcript
        time.sleep(0.25)
        transcript = "this is a placeholder transcription from google speech"
        logger.info(f"Finished transcription (len={len(transcript)})")
        return transcript
