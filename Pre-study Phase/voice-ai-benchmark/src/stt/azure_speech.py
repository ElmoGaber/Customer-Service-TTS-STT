from pathlib import Path
from .placeholder_base import BaseSTT
from src.utils.logger_config import get_logger
import time

logger = get_logger('azure_speech')


class AzureSpeechSTT(BaseSTT):
    def __init__(self, config: dict = None):
        super().__init__(config or {})

    def transcribe(self, audio_path: Path) -> str:
        logger.info(f"Starting local placeholder transcription for {audio_path}")
        time.sleep(0.30)
        transcript = "this is a placeholder transcription from azure speech"
        logger.info("Finished transcription")
        return transcript
