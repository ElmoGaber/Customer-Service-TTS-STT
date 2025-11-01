import os
from utils.logger import setup_logger
from utils.model_loader import load_tts_model
from utils.synthesizer import synthesize_text
from utils.evaluator import evaluate_synthesis
from utils.io_utils import read_text, save_json

# ========================
# Setup
# ========================
logger = setup_logger()
logger.info("Starting XTTS-v2 Smoke Test...")

MODEL_PATH = "models/xtts_v2"
OUTPUT_JSON = "outputs/metrics/tts_week2.json"

texts = {
    "en": read_text("samples/en.txt"),
    "ar": read_text("samples/ar.txt")
}

# ========================
# Run
# ========================
tts, device = load_tts_model()
logger.info(f"Model loaded on {device}")

results = {}

for lang, text in texts.items():
    logger.info(f"Processing {lang} sample...")
    output_file = f"outputs/audio/{lang}_output.wav"

    latency, size_kb = synthesize_text(tts, text, lang, output_file)
    metrics = evaluate_synthesis(text, latency, size_kb)

    results[lang] = {
        "output_file": output_file,
        **metrics
    }
    logger.info(f"Done {lang} | Latency: {latency:.2f}s | Size: {size_kb:.1f} KB")

save_json(results, OUTPUT_JSON)
logger.info(f"Results saved to {OUTPUT_JSON}")
print("✅ Smoke test finished. Check logs and metrics.")
