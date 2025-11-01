import pytest
from saudi_stt.audio_utils import enhance_saudi_pronunciation

def test_enhance_saudi_pronunciation():
    word = "شلونك"
    result = enhance_saudi_pronunciation(word)
    assert isinstance(result, str)
    assert len(result) > 0
