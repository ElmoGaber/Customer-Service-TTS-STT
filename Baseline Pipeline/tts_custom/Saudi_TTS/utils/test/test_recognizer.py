import pytest
from saudi_stt.recognizer import transcribe_saudi_audio

def test_saudi_transcribe_basic():
    result = transcribe_saudi_audio(b"FakeAudioData")
    assert isinstance(result, str)
