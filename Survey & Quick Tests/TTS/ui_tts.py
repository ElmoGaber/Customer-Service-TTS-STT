import gradio as gr
from TTS.api import TTS
import os, time

MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
tts = TTS(MODEL_NAME)

def generate_audio(text, language):
    output_path = f"outputs/audio/{language}_ui.wav"
    os.makedirs("outputs/audio", exist_ok=True)
    start = time.time()
    tts.tts_to_file(text=text, file_path=output_path, language=language)
    end = time.time()
    latency = end - start
    return output_path, f"⏱️ Latency: {latency:.2f}s"

demo = gr.Interface(
    fn=generate_audio,
    inputs=[gr.Textbox(label="Enter Text"), gr.Radio(["en", "ar"], label="Language")],
    outputs=[gr.Audio(label="Generated Speech"), gr.Textbox(label="Metrics")],
    title="🗣️ XTTS Multilingual Demo"
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861)
