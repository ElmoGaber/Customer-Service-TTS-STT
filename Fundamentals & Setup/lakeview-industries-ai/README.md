---
title: Lakeview Industries AI
emoji: 🏭
colorFrom: blue
colorTo: green
sdk: docker
app_file: server.py
pinned: false
---



# IronPath Orchestrator — V2 (Lean, Voice-Ready, Modular)

---
title: Lakeview Industries AI
emoji: 🏭
colorFrom: blue
colorTo: green
sdk: docker
app_file: server.py
pinned: false
---


A fresh scaffold for your troubleshooting assistant with **GPT Realtime** (voice), **LangGraph** routing,
and **no rigid JSON**. Outputs are compact markdown: **BLUF**, **Steps**, **Checks**, **Safety**, **If no improvement**.

## What’s included
- **FastAPI** backend with minimal endpoints: `/api/session/start`, `/api/session/status`, `/api/session/act`, `/api/stt`.
- **LangGraph** with 6 nodes: `intake_router → sme → safety → decision → [report] → [notify]`.
- **Confirm gate** via `REQUIRE_CONFIRM_BEFORE_NOTIFY=1`.
- **Realtime placeholder**: a `/api/realtime/ws` endpoint stub to bridge to the OpenAI Realtime API (WebSocket/WebRTC).
- **Tool registry placeholder**: `web_search`, `read_plc`, `fetch_order` (stubs).
- **Report** generator that produces a one-page HTML note saved to `./sessions` (or S3, if configured).
- **Email** notifier (SendGrid) that sends a short BLUF-only message with the link to the report.

## Quick start (macOS)
```bash
# Python
brew install python@3.11
python3 -m venv .venv && source .venv/bin/activate
pip install -U pip && pip install -r requirements.txt

# Environment
cp .env.example .env
# Fill OPENAI_API_KEY (and SENDGRID/S3 if you want).

# Run backend
uvicorn server:app --reload --port 8000
# Swagger: http://127.0.0.1:8000/docs
```

## Realtime notes
This scaffold **stubs** `/api/realtime/ws` and the Realtime client in `orchestrator/llm.py`.
Follow OpenAI Realtime docs to:
- Create a Realtime session (WebSocket or WebRTC) for duplex audio.
- Register `tools.py` functions so the model can call `web_search`, `read_plc`, etc.
- Stream TTS back to the operator. (Browser WebRTC or WS pull.)

## Testing (no UI required)
```bash
curl -s -X POST http://127.0.0.1:8000/api/session/start   -H 'Content-Type: application/json'   -d '{"user_input":"Slitter curl; speed 30→25; tensions 100/90; PPE ok."}'

# Then poll status, expect BLUF and steps:
curl -s "http://127.0.0.1:8000/api/session/status?session_id=sess_..." | jq

# If decision requires confirm (and REQUIRE_CONFIRM_BEFORE_NOTIFY=1):
curl -s -X POST http://127.0.0.1:8000/api/session/act   -H 'Content-Type: application/json'   -d '{"session_id":"sess_...","action":"confirm"}'
```
