import gradio as gr
from interface.interface import ModelInterface
from interface.audio_pipeline import AudioChatPipeline
from utils import setup_logger, get_model_path

# إعداد اللوجر
logger = setup_logger()
logger.info("🚀 Starting AI Voice Assistant...")

# تحميل الموديلات
stt_model = ModelInterface(get_model_path("stt"), "stt").load_model()
llm_model = ModelInterface(get_model_path("llm"), "llm").load_model()
tts_model = ModelInterface(get_model_path("tts"), "tts").load_model()
eq_ar_en = ModelInterface(get_model_path("eq_ar_en"), "equalizer").load_model()
eq_saudi = ModelInterface(get_model_path("eq_saudi"), "equalizer").load_model()

# إنشاء الـ pipeline
pipeline = AudioChatPipeline(stt_model, llm_model, tts_model, eq_ar_en)

logger.info("✅ All models loaded successfully.")

# دالة التفاعل
def chat_with_voice(audio_input, model_choice):
    logger.info(f"🎤 Received audio input, Equalizer: {model_choice}")
    pipeline.eq = eq_saudi if model_choice == "Saudi" else eq_ar_en
    final_audio = pipeline.process_audio_input(audio_input)
    logger.info("✅ Response generated and processed.")
    return final_audio

# واجهة Gradio
iface = gr.Interface(
    fn=chat_with_voice,
    inputs=[
        gr.Audio(source="microphone", type="filepath", label="🎤 Speak Here"),
        gr.Radio(["Saudi", "Arabic/English"], label="🎚️ Choose Equalizer")
    ],
    outputs=gr.Audio(type="numpy", label="🔊 AI Response"),
    title="AI Voice Assistant (Offline)",
    description="Fully offline LLM + STT + TTS + Equalizer pipeline."
)

logger.info("🟢 Launching Gradio Interface...")
iface.launch(server_name="0.0.0.0", server_port=7860)
