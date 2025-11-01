🗣️ XTTS Fine-Tuning & Voice Customization Guide
🎯 أولًا: نفهم إحنا واقفين فين
عندك حاليًا 3 أنظمة أساسية في مشروعك:


| النظام                   | الوظيفة                      | الموديل المستخدم | نوع المخرجات |
| :----------------------- | :--------------------------- | :--------------- | :----------- |
| **TTS (Text-to-Speech)** | تحويل النص إلى صوت           | `XTTS`           | صوت          |
| **STT (Speech-to-Text)** | تحويل الصوت إلى نص           | `Whisper`        | نص           |
| **Saudi Localization**   | تخصيص اللهجة والنغمة (سعودي) | يعتمد على `XTTS` | صوت مخصص     |



🔍 ثانياً: التوضيح الأساسي
🎙️ Whisper (STT)
وظيفته الوحيدة: تحويل الصوت إلى نص.

لا يحتوي على أي عنصر خاص بالصوت الناتج (لا ذكوري ولا أنثوي).

بالتالي لا يمكن عمل fine-tuning عليه لإنتاج صوت جديد.

✅ النتيجة:

Whisper = ملوش علاقة بالصوت أو النغمة. خارج موضوع الـ voice تمامًا.

🔊 XTTS (TTS)
هنا نقدر نتحكم في النغمة، الصوت، واللهجة.

🧩 الحالة 1 — استخدام الـ Model الجاهز
تقدر تستخدم الـ XTTS مباشرة باختيار:

speaker="male_en_1" → صوت ذكوري

speaker="female_en_2" → صوت أنثوي

لكن الصوت مش فريد — موجود عند كل اللي بيستخدم نفس الموديل.

🧠 الحالة 2 — Fine-Tuning / Voice Cloning
لو هدفك تعمل صوت مميز خاص بالمشروع (Localization / Brand Voice):
يبقى الحل هو Fine-tuning على بيانات صوتك أنت.


🎧 ثالثا: إعداد البيانات الصوتية
كل جملة صوتية لازم يكون ليها ملفين:

001.wav   ← ملف الصوت

001.txt   ← النص المنطوق داخل الصوت


📌 مواصفات التسجيل:
جودة الصوت: 16 kHz، mono.

لا يوجد noise أو echo.

الجمل قصيرة (3 – 8 ثواني).

استخدم ميكروفون ثابت.

⚙️ خامساً: إعداد بيئة العمل

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate   # أو .\venv\Scripts\activate على Windows

# تثبيت مكتبة Coqui TTS
pip install TTS==0.21.1
🧠 سادساً: ملف إعدادات التدريب (Config)
📄 configs/xtts_finetune_config.json

{
  "output_path": "output/model",
  "datasets": [
    {
      "name": "male_voice",
      "path": "data/male",
      "language": "en"
    },
    {
      "name": "female_voice",
      "path": "data/female",
      "language": "en"
    },
    {
      "name": "saudi_voice",
      "path": "data/saudi",
      "language": "ar"
    }
  ],
  "batch_size": 8,
  "num_epochs": 10,
  "use_cuda": true,
  "save_every_epoch": true,
  "model_name": "tts_models/multilingual/multi-dataset/xtts_v2"
}
🧩 سابعاً: كود التدريب
📄 scripts/train_xtts_finetune.py

from TTS.trainer import Trainer, TrainerArgs
from TTS.config.shared_configs import load_config
import os

if __name__ == "__main__":
    config_path = "configs/xtts_finetune_config.json"
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
🧪 ثامناً: تشغيل التدريب

python scripts/train_xtts_finetune.py
سيبدأ التدريب تلقائيًا على بيانات الصوت.
كل Epoch جديدة ستُنتج checkpoint داخل:



output/model/
🔊 تاسعاً: استخدام الموديل المخصص
بعد انتهاء التدريب استخدم الموديل الجديد:

from TTS.api import TTS

tts = TTS(model_path="output/model")

tts.tts_to_file(
    text="مرحبًا، هذا صوتنا الخاص بالمشروع.",
    file_path="output/custom_voice.wav",
    speaker="male_voice"
)
💎 عاشراً: تحسين النغمة واللهجة
يمكنك تعديل الخصائص الصوتية أثناء التوليد:


tts.tts_to_file(
    text="Hello world!",
    file_path="output/test.wav",
    speaker="female_voice",
    speaker_wav="data/female/001.wav",
    language="en",
    speed=1.1,       # سرعة النطق
    emotion="happy"  # العاطفة (لو مدعومة)
)
🔗 النتيجة النهائية
هتحصل على:


output/custom_voice.wav
وده الصوت اللي زميلك هيستخدمه في الـ GUI Avatar لعمل Lip Sync
(يُفضل حفظه بصيغة .wav أو .ogg لضمان جودة المزامنة الصوتية).

💬 الخلاصة

| العنصر                 | الوضع الحالي         | هل يحتاج داتا جديدة؟ | النتيجة                          |
| :--------------------- | :------------------- | :------------------- | :------------------------------- |
| **Whisper (STT)**      | لتحويل صوت → نص      | ❌ لا                 | لا علاقة بالصوت                  |
| **XTTS (TTS)**         | لتحويل نص → صوت      | ✅ نعم                | يعمل Fine-tuning لإنتاج صوت مميز |
| **Saudi Localization** | تخصيص النغمة واللهجة | ✅ جزئيًا             | استخدم بيانات باللهجة السعودية   |


🧠 الفهم التقني النهائي

| الهدف                    | الحل                                        |
| :----------------------- | :------------------------------------------ |
| صوت ذكر وأنثى عام        | استخدم Presets الجاهزة في XTTS              |
| صوت مميز خاص بالمشروع    | Fine-tuning لـ XTTS بصوت مخصص               |
| لهجة محددة (سعودي مثلًا) | اجمع بيانات صوت باللهجة المطلوبة            |
| تحكم في النغمة والتون    | عدّل الـ `pitch` و`prosody` أثناء inference |


