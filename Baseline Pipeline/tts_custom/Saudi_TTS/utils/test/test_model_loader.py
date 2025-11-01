import pytest
from saudi_stt.model_loader import load_saudi_model

def test_saudi_model_load():
    model = load_saudi_model()
    assert model is not None
