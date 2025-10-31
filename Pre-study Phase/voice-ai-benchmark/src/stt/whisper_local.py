from pathlib import Path
from .placeholder_base import BaseSTT
from src.utils.logger_config import get_logger
import time

logger = get_logger('whisper_local')

try:
    import whisper
except Exception:
    whisper = None


class WhisperLocalSTT(BaseSTT):
    def __init__(self, config: dict = None):
        super().__init__(config or {})
        self.model_name = (config or {}).get('model', 'small')
        self.model = None

    def _load_model(self):
        if whisper is None:
            logger.warning('whisper package not available, using placeholder behavior')
            return
        if self.model is None:
            logger.info(f'Loading whisper model: {self.model_name}')
            self.model = whisper.load_model(self.model_name)

    def transcribe(self, audio_path: Path) -> str:
        logger.info(f"Starting whisper_local transcription for {audio_path}")
        self._load_model()
        if self.model is None:
            # fallback placeholder
            time.sleep(0.4)
            return "this is a placeholder transcription from whisper local"

        start = time.perf_counter()
        res = self.model.transcribe(str(audio_path))
        elapsed = (time.perf_counter() - start) * 1000
        logger.info(f"Whisper finished in {elapsed:.1f}ms")
        return res.get('text', '')