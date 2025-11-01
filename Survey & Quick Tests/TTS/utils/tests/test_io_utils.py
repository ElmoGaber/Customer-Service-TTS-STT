import pytest
from tts.io_utils import save_audio, load_audio
import tempfile
import os

def test_save_and_load_audio():
    """يتأكد من حفظ وقراءة ملف الصوت"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    save_audio(b"dummydata", temp_file.name)
    data = load_audio(temp_file.name)
    os.unlink(temp_file.name)
    assert data.startswith(b"dummy"), "Audio data mismatch"
