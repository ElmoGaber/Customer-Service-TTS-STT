# core/tts_runner.py
import time
import os
from TTS.api import TTS
from utils.logger import setup_logger
from utils.file_manager import save_bytes
from utils.json_utils import save_json
from configs.settings import XTTS_MODEL_DIR, AUDIO_OUT, METRICS_OUT

logger = setup_logger()

def load_tts(model_path: str = XTTS_MODEL_DIR):
    """
    Load TTS model once. If you use TTS.api it will handle device selection.
    """
    logger.info("Loading TTS model from %s", model_path)
    tts = TTS(model_path, gpu=False)  # set gpu=True if cuda available
    logger.info("TTS model loaded")
    return tts

def tts_generate_to_file(tts_model, text: str, speaker: str = None, language: str = None, out_path: str = None):
    """
    generate tts and save to out_path; return metrics dict
    """
    os.makedirs(AUDIO_OUT, exist_ok=True)
    if out_path is None:
        safe_name = text[:40].replace(" ", "_").replace("/", "_")
        out_path = os.path.join(AUDIO_OUT, f"tts_{int(time.time())}_{safe_name}.wav")
    logger.info("TTS generating to %s", out_path)
    start = time.time()
    # using tts.tts_to_file. If your TTS supports return_bytes, you may use that
    tts_model.tts_to_file(text=text, file_path=out_path, speaker=speaker, language=language)
    latency = time.time() - start
    size_kb = os.path.getsize(out_path) / 1024
    metrics = {
        "text": text,
        "speaker": speaker,
        "language": language,
        "out_path": out_path,
        "latency_s": latency,
        "size_kb": size_kb
    }
    # save metrics
    os.makedirs(METRICS_OUT, exist_ok=True)
    fname = os.path.join(METRICS_OUT, f"tts_metrics_{int(time.time())}.json")
    save_json(fname, metrics)
    logger.info("TTS metrics saved to %s", fname)
    return metrics

# convenience wrapper for streaming bytes (if TTS supports returning bytes)
def tts_generate_bytes(tts_model, text: str, **kwargs) -> bytes:
    """
    If TTS has method returning bytes (change for your TTS implementation).
    This is placeholder: many TTS libs don't support return_bytes; you may read file bytes instead.
    """
    tmp_out = tts_generate_to_file(tts_model, text, out_path=os.path.join(AUDIO_OUT, "tmp_stream.wav"), **kwargs)
    with open(tmp_out["out_path"], "rb") as f:
        data = f.read()
    return data
