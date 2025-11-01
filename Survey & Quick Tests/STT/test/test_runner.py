import subprocess
import pytest
from core.whisper_runner import run_whisper_cli

def test_whisper_cli_runs_without_error(tmp_path):
    """يتأكد إن أمر الـ Whisper CLI بيشتغل وبيطلع ملف JSON أو نص بدون كراش"""
    sample_audio = "samples/short.wav"
    output_file = tmp_path / "out.json"

    result = run_whisper_cli(sample_audio, output_path=str(output_file))
    assert result.returncode == 0, f"Whisper CLI failed: {result.stderr}"

    assert output_file.exists(), "Output file was not created"
