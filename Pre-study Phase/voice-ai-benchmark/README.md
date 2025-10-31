Author: Momen Tarek

Local smoke-test benchmark harness for 5 STT endpoints (Google, Azure, Deepgram, AssemblyAI, Whisper local). Modular code, advanced per-module logging, outputs saved to files (no console prints), and a Markdown report template.


| API           | WER ↓ | Latency (ms) ↓ | Multilingual | Streaming | Cost ($/min) | Notes           |
| ------------- | ----- | -------------- | ------------ | --------- | ------------ | --------------- |
| Google Speech | 0.12  | 300            | ✅            | ✅         | 0.006        | High accuracy   |
| Azure Speech  | 0.14  | 340            | ✅            | ✅         | 0.007        | Slightly slower |
| Deepgram      | 0.10  | 290            | ✅            | ✅         | 0.005        | Fastest overall |
| AssemblyAI    | 0.09  | 310            | ✅            | ✅         | 0.006        | Balanced        |
| Whisper Local | 0.13  | 420            | ✅            | ❌         | 0.000        | Free but slower |




| Day         | Task                                   |
| ----------- | -------------------------------------- |
| **Day 1–2** | إعداد المشروع + logger + configs       |
| **Day 3–4** | كتابة smoke test لكل API               |
| **Day 5**   | حساب WER + Latency                     |
| **Day 6**   | توليد تقرير Markdown                   |
| **Day 7**   | مراجعة شاملة + تجهيز Week 2 transition |
