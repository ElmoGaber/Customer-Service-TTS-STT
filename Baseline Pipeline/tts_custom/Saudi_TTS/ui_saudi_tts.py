import gradio as gr
import torch, torchaudio, os
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

MODEL_DIR = "models/saudi-tts"
CONFIG_FILE = os.path.join(MODEL_DIR, "config.json")
SPEAKER_FILE = os.path.join(MODEL_DIR, "speaker.wav")

config = XttsConfig()
config.load_json(CONFIG_FILE)
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_dir=MODEL_DIR)
model.cuda()

gpt_latent, speaker_emb = model.get_conditioning_latents(audio_path=[SPEAKER_FILE])

def saudi_generate(text):
    os.makedirs("outputs/audio", exist_ok=True)
    output_path = "outputs/audio/saudi_ui.wav"
    out = model.inference(text, "ar", gpt_latent, speaker_emb, temperature=0.75)
    torchaudio.save(output_path, torch.tensor(out["wav"]).unsqueeze(0), 24000)
    return output_path

demo = gr.Interface(
    fn=saudi_generate,
    inputs=gr.Textbox(label="اكتب نص باللهجة السعودية"),
    outputs=gr.Audio(label="النطق باللهجة السعودية"),
    title="🇸🇦 Saudi TTS Demo",
    description="حوّل النص السعودي إلى صوت واقعي باللهجة المحلية."
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7862)
