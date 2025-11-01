# core/stt_runner.py
import time
import subprocess
import os
from utils.logger import setup_logger
from utils.json_utils import save_json
from configs.settings import WHISPER_MODEL, METRICS_OUT, AUDIO_OUT
from jiwer import wer

logger = setup_logger()

def run_whisper_cli(audio_path: str, model_path: str = WHISPER_MODEL) -> dict:
    """
    Run whisper.cpp CLI and return transcript and latency.
    Assumes whisper-cli exists at whisper.cpp/build/bin/whisper-cli
    """
    cmd = f"./whisper.cpp/build/bin/whisper-cli -m {model_path} -f {audio_path}"
    logger.info("Running whisper CLI: %s", cmd)
    start = time.time()
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    latency = time.time() - start
    if res.returncode != 0:
        logger.error("Whisper CLI failed: %s", res.stderr)
        return {"success": False, "stderr": res.stderr, "latency": latency}
    transcript = res.stdout.strip()
    logger.info("Whisper result len=%d, latency=%.3fs", len(transcript), latency)
    return {"success": True, "transcript": transcript, "latency": latency}

def evaluate_transcript(transcript: str, reference: str) -> float:
    # uses jiwer to compute WER
    try:
        score = wer(reference, transcript)
    except Exception as e:
        logger.exception("Error calculating WER: %s", e)
        score = 1.0
    logger.info("WER computed: %.3f", score)
    return score

def smoke_test(audio_path: str, reference: str = None, save_metrics: bool = True):
    res = run_whisper_cli(audio_path)
    metrics = {
        "audio": audio_path,
        "success": res.get("success", False),
        "latency_s": res.get("latency", None),
        "transcript": res.get("transcript", "")
    }
    if reference:
        metrics["wer"] = evaluate_transcript(metrics["transcript"], reference)
    if save_metrics:
        os.makedirs(METRICS_OUT, exist_ok=True)
        fname = os.path.join(METRICS_OUT, f"stt_metrics_{os.path.basename(audio_path)}.json")
        save_json(fname, metrics)
        logger.info("STT metrics saved to %s", fname)
    return metrics
