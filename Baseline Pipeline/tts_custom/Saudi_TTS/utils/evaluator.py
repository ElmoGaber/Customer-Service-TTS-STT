def evaluate_sample(text, latency, size_kb):
    return {
        "text": text,
        "latency_sec": latency,
        "file_size_kb": size_kb,
        "naturalness_notes": "Check subjectively after listening."
    }
