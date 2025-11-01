import os
import time
import json
import logging
from jiwer import wer
import subprocess

# ========================
# Logger setup
# ========================
log_file = "logs/whisper.log"
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ========================
# Config
# ========================
MODEL_PATH = "whisper.cpp/models/ggml-large-v3-turbo.bin"
SAMPLES = ["samples/short.wav", "samples/long.wav"]
GROUND_TRUTH = {
    "samples/short.wav": "your short transcript here",
    "samples/long.wav": "your long transcript here"
}
OUTPUT_JSON = "outputs/metrics/stt_week2.json"
os.makedirs("outputs/metrics", exist_ok=True)

# ========================
# Function: run inference
# ========================
def run_whisper(audio_path: str, model_path: str):
    """Run whisper.cpp binary inference"""
    start = time.time()
    
    # command assumes whisper-cli is built
    cmd = f"./whisper.cpp/build/bin/whisper-cli -m {model_path} -f {audio_path}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    latency = time.time() - start
    transcript = result.stdout.strip()
    
    return transcript, latency

# ========================
# Function: evaluate sample
# ========================
def evaluate_sample(audio_path: str):
    transcript, latency = run_whisper(audio_path, MODEL_PATH)
    reference = GROUND_TRUTH[audio_path]
    error = wer(reference, transcript)
    
    logging.info(f"{audio_path} | WER: {error:.3f} | Latency: {latency:.2f}s")
    
    return {
        "file": audio_path,
        "transcript": transcript,
        "reference": reference,
        "wer": error,
        "latency": latency
    }

# ========================
# Main: run smoke test
# ========================
def smoke_test():
    results = []
    for audio in SAMPLES:
        result = evaluate_sample(audio)
        results.append(result)
    
    # Save to JSON
    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=4)
    
    logging.info("Smoke test completed. Results saved to " + OUTPUT_JSON)
    print("Smoke test done. Check logs and outputs.")

if __name__ == "__main__":
    smoke_test()
