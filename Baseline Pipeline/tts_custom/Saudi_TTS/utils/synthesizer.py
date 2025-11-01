import torch
import torchaudio
import os
import time

def synthesize_saudi_tts(model, text, lang, speaker_file, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    start_time = time.time()
    gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=[speaker_file])
    out = model.inference(text, lang, gpt_cond_latent, speaker_embedding, temperature=0.75)
    latency = time.time() - start_time

    torchaudio.save(output_path, torch.tensor(out["wav"]).unsqueeze(0), 24000)
    size_kb = os.path.getsize(output_path) / 1024
    return latency, size_kb
