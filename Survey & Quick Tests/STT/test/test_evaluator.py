import pytest
from core.whisper_evaluator import calculate_wer

def test_calculate_wer_basic():
    ref = "السلام عليكم ورحمة الله"
    hyp = "السلام عليكم ورحمة"
    wer = calculate_wer(ref, hyp)
    assert 0 <= wer <= 1
