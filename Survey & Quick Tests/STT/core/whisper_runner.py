import subprocess
import time

def run_whisper(audio_path: str, model_path: str):
    """Run whisper.cpp binary inference"""
    start_time = time.time()
    cmd = f"./whisper.cpp/build/bin/whisper-cli -m {model_path} -f {audio_path}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    latency = time.time() - start_time
    transcript = result.stdout.strip()
    return transcript, latency
