import subprocess
import pytest
import json
import os

def test_smoke_whisper_full_pipeline(tmp_path):
    """اختبار شامل بسيط للتأكد إن كل شيء شغال"""
    input_audio = "samples/short.wav"
    output_json = tmp_path / "whisper_output.json"

    result = subprocess.run(
        ["python", "core/whisper_runner.py", input_audio, str(output_json)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"CLI crashed: {result.stderr}"

    assert output_json.exists(), "Whisper output JSON not found"
    with open(output_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "transcription" in data, "Missing transcription in output"
