import os
import time

def synthesize_text(tts, text, lang, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    start = time.time()
    tts.tts_to_file(text=text, file_path=output_path, language=lang)
    latency = time.time() - start
    size_kb = os.path.getsize(output_path) / 1024
    return latency, size_kb
