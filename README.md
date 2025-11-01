# Customer Service Builder (Voice Interaction)

## 📌 Project Description
This project aims to build a **Customer Service Builder** that relies on **voice interaction** instead of text only.  
Customers can **speak directly** with the system, and the system will respond with a **natural-sounding voice** by integrating:

- **Speech-to-Text (STT)** → Convert customer speech into text.  
- **Text-to-Speech (TTS)** → Convert system responses into speech.  

The system is designed to be modular, scalable, and user-friendly, with future integration of **RAG (Retrieval-Augmented Generation)** and **LLM fine-tuning**.

---

## 🎯 Goals
- Provide an **intelligent customer service system** that can handle queries via **voice**.  
- Evaluate and compare multiple **speech models** for accuracy, latency, and user experience.  
- Deliver a working **MVP** with voice in/out and customer interaction scenarios.  

---

## 🛠️ Tech Stack
- **Backend**: Python, FastAPI  
- **AI/ML**: PyTorch, HuggingFace Transformers, SpeechBrain, Coqui, OpenAI Whisper  
- **Database**: MongoDB, Weaviate/Qdrant (VectorDB)  
- **Frontend/Interface**: Gradio / Web Integration  
- **Optional**: Avatar integration with lip-sync  

---

## 📅 Timeline (8 Weeks)
- **Pre-study (Before Semester)**: Tested 10 APIs for speech models, compared accuracy, latency, complexity, and UX.  
- **Week 1**: Environment setup + Fundamentals of STT/TTS.  
- **Week 2**: Model survey & smoke tests → shortlist best STT/TTS models.  
- **Week 3**: Baseline STT + TTS pipeline demo.  
- **Week 4**: Light avatar integration (lip-sync + audio playback).  
- **Week 5**: Real-time microphone streaming integration.  
- **Week 6**: Error analysis & early user testing.  
- **Week 7**: Benchmarking & cost analysis.  
- **Week 8**: Final prototype with multi-scenario customer service demo.  

---

## 🚀 MVP Features
- Customer speaks → system understands via **STT**.  
- System generates response (text) → converted to **TTS voice output**.  
- Optional avatar for more engaging interaction.  
