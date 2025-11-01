def evaluate_synthesis(text, latency, size_kb):
    # يمكن لاحقًا نضيف تقييم ذاتي أو Subjective Metrics
    return {
        "input_text": text,
        "latency_sec": latency,
        "file_size_kb": size_kb,
        "naturalness_notes": "Add subjective notes after listening."
    }
