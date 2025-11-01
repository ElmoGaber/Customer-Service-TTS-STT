# مقارنة موديلات Audio-to-Audio

| الخاصية / Feature | Kokoro-Conversational (asif00) | Voila-Chat (maitrix-org) | Speech-Conversion (Amirhossein75) |
|------------------|-------------------------------|--------------------------|----------------------------------|
| **الوصف / Description** | نموذج AI للمحادثة الصوتية يعمل **Realtime** على الجهاز. يجمع بين الكشف عن الصوت، تحويل الكلام إلى نص، نموذج اللغة، وتقنيات TTS. | مجموعة موديلات Foundation للـ Voice-Language. تصميم **End-to-End** مع Transformer هرمية لتحسين التفاعل البشري-الآلي وتقليل التأخير. | تحويل صوت إلى صوت آخر (**Voice Conversion**) باستخدام **SpeechT5** و **HiFiGAN**، يعتمد على X-vector لتشكيل الصوت الهدف. |
| **المهام / Tasks** | Speech-to-Speech، Conversational AI، Voice Chat، Realtime | Audio Chat، Text-to-Speech، ASR، Speech Translation، Persona-driven interaction | Voice Conversion، Speech-to-Speech (any-to-any) |
| **اللغات / Languages** | 13 لغة | 6 لغات | الإنجليزية فقط (CMU ARCTIC dataset) |
| **المدخلات / Inputs** | صوت المستخدم مباشرة (microphone) | صوت المستخدم مباشرة أو ملف صوتي | ملف صوت المصدر + ملف صوت الهدف (reference) |
| **المخرجات / Outputs** | صوت مستجيب بشكل طبيعي وواقعي | صوت مع محتوى محادثة/شخصية مُفصلة، TTS عالي الجودة | تحويل الصوت المصدر إلى صوت الهدف مع الحفاظ على المحتوى |
| **أداء / Performance** | AMD Ryzen 5600G، 16 GB، No-GPU → **Latency ≈ 1.5s** للرد | Latency ≈ 195 ms، WER: 2.7%-4.8%، TTS WER: 2.8%-3.2% | Real-time أسرع مع GPU، جودة التحويل تعتمد على جودة الموديل و X-vector |
| **نماذج داخلية / Internal Models** | - VAD: Pyannote 3.0<br>- STT: Whisper-tiny.en<br>- LM: Ollama qwen2.5<br>- TTS: Kokoro-82M | - ASR & TTS & Chat: Voila-base, Voila-chat, Voila-autonomous-preview<br>- Tokenizer: Voila-Tokenizer | - SpeechT5 VC encoder-decoder<br>- HiFiGAN vocoder<br>- Speaker embeddings: ECAPA X-vector |
| **متطلبات تشغيل / Requirements** | Python 3.8+, eSpeak NG, Ollama, Git LFS | Python 3.10+, PyTorch, Transformers, Datasets, Soundfile | Python 3.10+, Transformers>=4.42, Datasets>=2.20, Torch>=2.1, Speechbrain>=1.0, Soundfile |
| **الترخيص / License** | MIT | MIT | Repository: Other / Base Models: MIT |
| **المخاطر / Risks** | - استهلاك موارد الجهاز<br>- عدم دقة الترجمة لبعض اللغات | - الأداء على لغات غير مدربة قد يكون أقل<br>- اعتماد على نموذج مركزي | - خطر الانتحال الصوتي بدون موافقة<br>- الأداء أقل على لهجات مختلفة أو بيئة ضوضاء |
| **الاستعمال / Usage** | محادثة صوتية مباشرة، بحث أو تطوير محلي | محادثة صوتية متقدمة، مشاريع أبحاث، TTS متعدد الشخصيات | تحويل صوت فرد لآخر، تجارب تعليمية وأبحاث، خدمة inference سريعة على GPU |
| **رابط GitHub / GitHub** | [asif00/Kokoro-Conversational](https://github.com/asiff00/On-Device-Speech-to-Speech-Conversational-AI) | [maitrix-org/Voila-chat](https://huggingface.co/maitrix-org/Voila-chat) | [Amirhossein75/Speech-Conversion](https://github.com/amirhossein-yousefi/speech-conversion) |
| **مقارنة الأداء / Benchmark** | Latency ~1.5s (CPU) | WER: 2.7%-4.8%, TTS WER: 2.8%-3.2% | جودة التحويل تعتمد على المرجع والصوت الهدف، أسرع مع GPU |

