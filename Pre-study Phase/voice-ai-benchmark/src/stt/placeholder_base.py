from abc import ABC, abstractmethod
from pathlib import Path


class BaseSTT(ABC):
    """Abstract base for STT providers. Each provider should implement transcribe(path) -> str"""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def transcribe(self, audio_path: Path) -> str:
        raise NotImplementedError