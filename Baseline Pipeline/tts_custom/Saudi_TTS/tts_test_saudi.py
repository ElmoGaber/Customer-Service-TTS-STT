import os
from utils.logger import setup_logger
from utils.io_utils import read_lines, save_json
from utils.model_loader import load_saudi_tts
from utils.synthesizer import synthesize_saudi_tts
from utils.evaluator import evaluate_sample

# ========================
# Setup
# ========================
logger = setup_logger()
logger.info("Starting Saudi TTS Smoke Test...")

MODEL_DIR = "models/saudi-tts"
SPEAKER_FILE = os.path.join(MODEL_DIR, "speaker.wav")
OUTPUT_JSON = "outputs/metrics/tts_week2_saudi.json"
OUTPUT_AUDIO_DIR = "outputs/audio"

# ========================
# Load Model
# ========================
model, device = load_saudi_tts(MODEL_DIR)
logger.info(f"Saudi TTS model loaded successfully on {device}")

# ========================
# Load Samples
# ========================
texts = read_lines("samples/ar.txt")
logger.info(f"Loaded {len(texts)} test samples.")

# ========================
# Inference & Evaluation
# ========================
results = {}

for idx, text in enumerate(texts):
    sample_id = f"sample_{idx+1}"
    output_file = os.path.join(OUTPUT_AUDIO_DIR, f"ar_{sample_id}.wav")

    logger.info(f"Generating audio for {sample_id}...")
    latency, size_kb = synthesize_saudi_tts(model, text, "ar", SPEAKER_FILE, output_file)

    metrics = evaluate_sample(text, latency, size_kb)
    results[sample_id] = {"output_file": output_file, **metrics}

    logger.info(f"Done {sample_id} | Latency: {latency:.2f}s | Size: {size_kb:.1f} KB")

# ========================
# Save Results
# ========================
save_json(results, OUTPUT_JSON)
logger.info(f"Results saved to {OUTPUT_JSON}")
print("✅ Saudi TTS Smoke Test finished. Check logs and metrics.")
