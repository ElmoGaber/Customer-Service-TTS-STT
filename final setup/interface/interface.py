import torch
from TTS.api import TTS
from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoProcessor

class ModelInterface:
    def __init__(self, model_path, model_type):
        self.model_path = model_path
        self.model_type = model_type
        self.model = None

    def load_model(self):
        """تحميل الموديل المناسب"""
        print(f"🔹 Loading {self.model_type} model from {self.model_path}...")

        if self.model_type == "tts":
            self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        elif self.model_type == "stt":
            model_id = "openai/whisper-small"
            self.model = pipeline("automatic-speech-recognition", model=model_id)
        elif self.model_type == "llm":
            from transformers import AutoModelForCausalLM, AutoTokenizer
            model_id = "mistralai/Mistral-7B-Instruct-v0.2"
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")
        elif self.model_type == "equalizer":
            # Equalizer يمكن اعتباره فلتر صوتي بسيط أو موديل تحويل نغمة
            self.model = None

        print(f"✅ {self.model_type} model loaded.")
        return self.model
