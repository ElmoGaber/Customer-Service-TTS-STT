import os
import torch
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

def load_saudi_tts(model_dir="models/saudi-tts"):
    config_path = os.path.join(model_dir, "config.json")
    config = XttsConfig()
    config.load_json(config_path)

    model = Xtts.init_from_config(config)
    model.load_checkpoint(config, checkpoint_dir=model_dir, use_deepspeed=False)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        model.cuda()

    return model, device
