from pathlib import Path
import os

    FORMAT: str = Field(default="pyaudio.paFloat32", env="FORMAT")
    CHANNELS: int = Field(default=1, env="CHANNELS")
    RATE: int = Field(default=16000, env="RATE")
    OUTPUT_SAMPLE_RATE: int = Field(default=24000, env="OUTPUT_SAMPLE_RATE")
    RECORD_DURATION: int = Field(default=5, env="RECORD_DURATION")
    SILENCE_THRESHOLD: float = Field(default=0.01, env="SILENCE_THRESHOLD")
    INTERRUPTION_THRESHOLD: float = Field(default=0.02, env="INTERRUPTION_THRESHOLD")
    MAX_SILENCE_DURATION: int = Field(default=1, env="MAX_SILENCE_DURATION")
    SPEECH_CHECK_TIMEOUT: float = Field(default=0.1, env="SPEECH_CHECK_TIMEOUT")
    SPEECH_CHECK_THRESHOLD: float = Field(default=0.02, env="SPEECH_CHECK_THRESHOLD")
    ROLLING_BUFFER_TIME: float = Field(default=0.5, env="ROLLING_BUFFER_TIME")
    TARGET_SIZE: int = Field(default=15, env="TARGET_SIZE")
    FIRST_SENTENCE_SIZE: int = Field(default=3, env="FIRST_SENTENCE_SIZE")
    PLAYBACK_DELAY: float = Field(default=0.005, env="PLAYBACK_DELAY")

    def setup_directories(self):
        """Create necessary directories if they don't exist"""
        self.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        self.VOICES_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

    class Config:
        env_file = r"D:\Desktop\Level 4 Semester 1\project\Light Avatar & Streaming Setup\Kokoro-Conversational\.env.template"
        env_file_encoding = "utf-8"


settings = Settings()


def configure_logging():
    """Configure logging to suppress all logs"""
    import logging
    import warnings

    warnings.filterwarnings("ignore")

    logging.getLogger().setLevel(logging.ERROR)

    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("PIL").setLevel(logging.ERROR)
    logging.getLogger("matplotlib").setLevel(logging.ERROR)
    logging.getLogger("torch").setLevel(logging.ERROR)
    logging.getLogger("tensorflow").setLevel(logging.ERROR)
    logging.getLogger("whisper").setLevel(logging.ERROR)
    logging.getLogger("transformers").setLevel(logging.ERROR)
    logging.getLogger("pyannote").setLevel(logging.ERROR)
    logging.getLogger("sounddevice").setLevel(logging.ERROR)
    logging.getLogger("soundfile").setLevel(logging.ERROR)
    logging.getLogger("uvicorn").setLevel(logging.ERROR)
    logging.getLogger("fastapi").setLevel(logging.ERROR)


configure_logging()
