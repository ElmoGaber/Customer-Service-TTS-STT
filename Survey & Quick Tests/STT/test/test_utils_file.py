import pytest
from utils.file_manager import ensure_dir, save_temp_file
import os

def test_ensure_dir_creates_path(tmp_path):
    target = tmp_path / "nested"
    ensure_dir(target)
    assert target.exists()

def test_save_temp_file(tmp_path):
    path = save_temp_file("hello world", tmp_path)
    assert os.path.exists(path)
