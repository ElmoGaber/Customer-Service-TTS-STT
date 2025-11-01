# Cognitive Voice Agent (CVA) - Starter
Modular local pipeline: STT (Whisper) -> LLM Router (Qwen3 / Mistral) -> TTS (XTTS) -> Avatar (lip-sync)

## Layout
- `core/` : STT / TTS / LLM wrappers & router
- `services/` : FastAPI app
- `utils/` : logging, IO helpers
- `models/` : place your model files here
- `outputs/` : generated audio & metrics
- `samples/` : audio samples for testing

## Quickstart
1. Create venv & install:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
