from TTS.api import TTS
import torch

def load_tts_model(model_name="tts_models/multilingual/multi-dataset/xtts_v2"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS(model_name, gpu=(device == "cuda"))
    return tts, device
