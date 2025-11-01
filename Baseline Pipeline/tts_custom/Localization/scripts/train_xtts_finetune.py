from TTS.trainer import Trainer, TrainerArgs
from TTS.config.shared_configs import load_config
import os

if __name__ == "__main__":
    config_path = "tts_finetune_config.json"
    config = load_config(config_path)

    output_path = config["output_path"]
    os.makedirs(output_path, exist_ok=True)

    trainer = Trainer(
        TrainerArgs(
            restore_path=None,
            continue_path=None,
            config_path=config_path
        )
    )

    print("🚀 Starting XTTS Fine-Tuning...")
    trainer.fit()
