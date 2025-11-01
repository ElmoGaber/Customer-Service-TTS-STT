import pytest
from tts.model_loader import load_model

def test_model_loads_successfully():
    """يتأكد إن الموديل بيتحمل بدون أخطاء"""
    model = load_model()
    assert model is not None, "Model failed to load"
    assert hasattr(model, "speak") or hasattr(model, "generate"), "Invalid TTS model interface"
