import gradio as gr
from core.whisper_runner import run_whisper
from core.whisper_evaluator import evaluate_transcript

def transcribe_audio(audio_file):
    transcript, latency = run_whisper(audio_file)
    return f"⏱️ Latency: {latency:.2f}s\n🗒️ Transcript:\n{transcript}"

demo = gr.Interface(
    fn=transcribe_audio,
    inputs=gr.Audio(type="filepath", label="Upload Audio File"),
    outputs="text",
    title="🎧 Whisper STT Demo",
    description="Upload an audio file and get automatic transcription."
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
