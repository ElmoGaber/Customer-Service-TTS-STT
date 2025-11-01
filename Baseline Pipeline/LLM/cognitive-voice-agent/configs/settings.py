# configs/settings.py
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
AUDIO_OUT = os.path.join(OUTPUT_DIR, "audio")
METRICS_OUT = os.path.join(OUTPUT_DIR, "metrics")

# STT model path (whisper cpp ggml or other)
WHISPER_MODEL = os.path.join(MODELS_DIR, "whisper", "ggml-large-v3-turbo.bin")

# TTS model path (XTTS fine-tuned or base)
XTTS_MODEL_DIR = os.path.join(MODELS_DIR, "xtts")

# LLM models (local indicators)
QWEN_MODEL = os.path.join(MODELS_DIR, "llm", "qwen3-4b.gguf")      # example
MISTRAL_MODEL = os.path.join(MODELS_DIR, "llm", "mistral-24b.gguf") # example

# Router thresholds
COMMAND_CONFIDENCE_THRESHOLD = 0.7

# FastAPI server settings
API_HOST = "0.0.0.0"
API_PORT = 8000
