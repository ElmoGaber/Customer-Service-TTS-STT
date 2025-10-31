# orchestrator/stt.py
from __future__ import annotations
from typing import Optional
import io

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore

from orchestrator.config import load_env
SETTINGS = load_env()

_client = None

def _client_ok() -> Optional[object]:
    global _client
    if _client is None and OpenAI is not None:
        kwargs = {}
        if SETTINGS.OPENAI_BASE_URL:
            kwargs["base_url"] = SETTINGS.OPENAI_BASE_URL
        _client = OpenAI(api_key=SETTINGS.OPENAI_API_KEY, **kwargs)
    return _client

def transcribe_chunk(file_bytes: bytes, filename: str = "audio.webm", mimetype: str = "audio/webm", language: Optional[str] = None) -> str:
    """
    Transcribe a short audio chunk to text using the configured STT model.
    Returns "" on silence or if STT is unavailable (fail-safe).
    """
    c = _client_ok()
    if not c or not file_bytes:
        return ""
    model = SETTINGS.STT_MODEL or "gpt-4o-mini-transcribe"

    try:
        # Use the new /audio/transcriptions endpoint via SDK (OpenAI python >= 1.0)
        # Fall back gracefully on older SDKs by returning empty text.
        buffer = io.BytesIO(file_bytes)
        buffer.name = filename  # SDK inspects .name to set filename
        args = {
            "model": model,
            "file": buffer,
        }
        if language:
            args["language"] = language

        resp = c.audio.transcriptions.create(**args)  # type: ignore[attr-defined]
        text = (getattr(resp, "text", None) or "").strip()
        return text
    except Exception:
        # Be conservative; we don't want STT to crash the flow
        return ""
