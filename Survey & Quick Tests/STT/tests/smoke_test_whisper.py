import sys
import os

# === Dynamic Imports ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)

from config.settings import MODEL_PATH, SAMPLES, GROUND_TRUTH, OUTPUT_JSON, LOG_FILE
from core.whisper_runner import run_whisper
from core.whisper_evaluator import evaluate_transcript
from utils.logger import setup_logger
from utils.json_utils import save_json

# === Setup Logger ===
logger = setup_logger(LOG_FILE)

def evaluate_sample(audio_path):
    transcript, latency = run_whisper(audio_path, MODEL_PATH)
    reference = GROUND_TRUTH[audio_path]
    error = evaluate_transcript(reference, transcript)

    logger.info(f"{audio_path} | WER: {error:.3f} | Latency: {latency:.2f}s")

    return {
        "file": audio_path,
        "transcript": transcript,
        "reference": reference,
        "wer": error,
        "latency": latency
    }

def smoke_test():
    logger.info("Starting Whisper Smoke Test...")
    results = [evaluate_sample(audio) for audio in SAMPLES]
    save_json(results, OUTPUT_JSON)
    logger.info("Smoke test completed. Results saved to metrics JSON.")
    logger.info("✅ Whisper pipeline verified successfully.")

if __name__ == "__main__":
    smoke_test()
