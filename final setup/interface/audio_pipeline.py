import torchaudio
import torch
import os
from utils import ensure_dir

class AudioChatPipeline:
    def __init__(self, stt_model, llm_model, tts_model, eq_model):
        self.stt = stt_model
        self.llm = llm_model
        self.tts = tts_model
        self.eq = eq_model

    def process_audio_input(self, audio_path):
        """خط المعالجة الكامل: STT → LLM → TTS → EQ"""
        ensure_dir("outputs/audio")

        # 1️⃣ تحويل الصوت لنص
        print("🎧 Running Speech-to-Text...")
        text = self.stt(audio_path)["text"]

        # 2️⃣ الرد باستخدام LLM
        print("🧠 Generating AI response...")
        inputs = self.llm.tokenizer(text, return_tensors="pt").to(self.llm.model.device)
        outputs = self.llm.model.generate(**inputs, max_new_tokens=100)
        response = self.llm.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # 3️⃣ تحويل النص لصوت
        print("🔊 Synthesizing speech...")
        output_path = "outputs/audio/final_output.wav"
        self.tts.tts_to_file(text=response, file_path=output_path, language="ar")

        # 4️⃣ تطبيق EQ (لو متاح)
        print("🎚️ Applying Equalizer (if available)...")
        waveform, sr = torchaudio.load(output_path)
        if self.eq:
            # هنا ممكن تعمل تعديل بسيط في الصوت (فلتر أو تأثير)
            waveform = torch.clamp(waveform * 1.05, -1.0, 1.0)
            torchaudio.save(output_path, waveform, sr)

        return output_path
