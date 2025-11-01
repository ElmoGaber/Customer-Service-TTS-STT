import pytest
from tts.synthesizer import synthesize_speech

def test_synthesize_output_type():
    """يتأكد إن الناتج بايتات صوت"""
    result = synthesize_speech("مرحبا بالعالم")
    assert isinstance(result, (bytes, bytearray)), "Output is not audio bytes"
    assert len(result) > 0, "Empty audio output"
