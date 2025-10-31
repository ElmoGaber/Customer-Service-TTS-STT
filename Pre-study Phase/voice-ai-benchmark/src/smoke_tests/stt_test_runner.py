import os
import time
import json
import logging
from src.utils.logger_config import get_logger
from src.evaluation.wer_calculator import calculate_wer
from src.evaluation.latency_checker import measure_latency
from src.utils.io_utils import load_audio_file

# إعداد اللوج العام
benchmark_logger = get_logger("benchmark", "logs/benchmark.log")

def run_smoke_test(api_name: str, audio_path: str):
    """
    Run smoke test for a given STT API.
    """
    logger = get_logger(api_name, f"logs/{api_name}.log")
    start_time = time.time()
    try:
        # تحميل الصوت
        audio_data, sr = load_audio_file(audio_path)

        # هنا مكان استدعاء API (placeholder)
        # لسه هنربط الـ APIs لاحقًا لما تدخل الـ keys
        # مؤقتًا هنرجّع نص وهمي للتجربة
        fake_transcript = "this is a test transcription"
        reference_text = "this is a test transcription"

        # حساب الـ WER (Word Error Rate)
        wer_score = calculate_wer(reference_text, fake_transcript)

        # حساب الـ Latency
        latency = measure_latency(start_time)

        result = {
            "api": api_name,
            "wer": round(wer_score, 3),
            "latency_ms": round(latency * 1000, 2),
            "status": "success",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        logger.info(f"{api_name} | WER={result['wer']} | Latency={result['latency_ms']} ms | Status=OK")
        return result

    except Exception as e:
        logger.error(f"{api_name} | ERROR: {str(e)}")
        return {
            "api": api_name,
            "wer": None,
            "latency_ms": None,
            "status": "failed",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

def main(audio_path: str):
    apis = ["google_speech", "azure_speech", "deepgram", "assemblyai", "whisper_local"]
    results = []

    for api in apis:
        benchmark_logger.info(f"Running smoke test for: {api}")
        res = run_smoke_test(api, audio_path)
        results.append(res)

    os.makedirs("outputs/metrics", exist_ok=True)
    output_path = "outputs/metrics/stt_metrics.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    benchmark_logger.info(f"All smoke tests completed. Results saved to {output_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run smoke tests for STT APIs")
    parser.add_argument("--sample", type=str, required=True, help="Path to test audio sample")
    args = parser.parse_args()

    main(args.sample)
