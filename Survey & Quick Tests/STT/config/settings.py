import os

# === General Paths ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

MODEL_PATH = os.path.join(BASE_DIR, "whisper.cpp/models/ggml-large-v3-turbo.bin")
SAMPLES = [
    os.path.join(BASE_DIR, "samples/short.wav"),
    os.path.join(BASE_DIR, "samples/long.wav")
]

GROUND_TRUTH = {
    SAMPLES[0]: "your short transcript here",
    SAMPLES[1]: "your long transcript here"
}

OUTPUT_JSON = os.path.join(BASE_DIR, "outputs/metrics/stt_week2.json")
LOG_FILE = os.path.join(BASE_DIR, "logs/whisper.log")

# === Ensure Directories Exist ===
os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
