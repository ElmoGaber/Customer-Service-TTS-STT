# server.py
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path
from typing import Optional, Dict

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from orchestrator import agents
from orchestrator.agents import normalize_markdown  # optional
from orchestrator.config import load_env
from orchestrator.graph_app import build_graph
from orchestrator.llm import chat_markdown, summarize_problem, summarize_incremental  # optional
from orchestrator.state import OrchestratorState

# --- ensure_sessions_dir with fallback ---
try:
    from orchestrator.storage_s3 import ensure_sessions_dir
except Exception:
    def ensure_sessions_dir():
        os.makedirs("sessions", exist_ok=True)

from orchestrator.tools import web_search
from orchestrator.scribe import append_event, build_and_save_report, save_markdown_report
from orchestrator import stt as stt_mod

# ---------------- Base paths & env ----------------
load_dotenv()
SETTINGS = load_env()

BASE_DIR = Path(__file__).resolve().parent
(SESS_DIR := BASE_DIR / "sessions").mkdir(parents=True, exist_ok=True)

# ---------------- App ----------------
app = FastAPI(title="Lakeview Industries AI")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ---------------- Static mounts ----------------
ensure_sessions_dir()
app.mount("/sessions", StaticFiles(directory="sessions", html=True), name="sessions")

# Serve UI under /ui (always) and redirect / -> /ui/ to avoid swallowing /api routes.
ui_dir = Path("ui")
if ui_dir.is_dir():
    app.mount("/ui", StaticFiles(directory=str(ui_dir), html=True), name="ui")

# Optional: serve /static for logos, etc.
static_dir = Path("static")
if static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Redirect root to /ui/ so operators land on the app, while keeping /api/* free.
@app.get("/", include_in_schema=False)
def root_redirect():
    # If there's no UI, show a tiny status page instead of redirecting.
    if not ui_dir.is_dir():
        return HTMLResponse("""
<!doctype html>
<meta charset="utf-8">
<title>Lakeview Industries AI</title>
<style>body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;padding:2rem}.box{max-width:720px;margin:0 auto}a{text-decoration:none;color:#0070f3}</style>
<div class="box">
  <h1>Lakeview Industries AI</h1>
  <p>✅ Server is running and the backend is ready.</p>
  <ul>
    <li><a href="/health" target="_blank">Check health endpoint</a></li>
    <li><a href="/docs" target="_blank">Open API Docs</a></li>
    <li><a href="/sessions" target="_blank">View saved reports</a></li>
  </ul>
</div>
""")
    return RedirectResponse("/ui/")

# ---------------- In-memory sessions ----------------
SESSIONS: Dict[str, OrchestratorState] = {}

# ---------------- Pydantic models ----------------
class StartReq(BaseModel):
    user_input: str
    language: Optional[str] = None
    area_hint: Optional[str] = None

class ActReq(BaseModel):
    session_id: str
    action: str  # "confirm" | "escalate" | "stop"

class RealtimeTokenReq(BaseModel):
    model: Optional[str] = None
    voice: Optional[str] = "verse"

class ScribeEventIn(BaseModel):
    session_id: str
    role: str
    text: str

class ScribeSummIn(BaseModel):
    session_id: str

class ScribeSaveIn(BaseModel):
    session_id: str
    markdown: str

# ---------------- LangGraph runner helper ----------------
def _run_once(graph, state: OrchestratorState) -> OrchestratorState:
    """Run one LangGraph step if possible, else return state unchanged."""
    if graph is None:
        return state
    if hasattr(graph, "invoke"):
        return graph.invoke(state)
    if callable(graph):
        return graph(state)
    return state

# ---------------- Lifecycle ----------------
@app.on_event("startup")
def _startup():
    ensure_sessions_dir()
    try:
        app.state.graph = build_graph()
        print("✅ Startup: graph built and app is ready", file=sys.stdout, flush=True)
    except Exception as e:
        import traceback
        traceback.print_exc()
        app.state.graph = None
        print(f"⚠️ Startup degraded (graph unavailable): {e}", file=sys.stderr, flush=True)

# ---------------- Health ----------------
@app.get("/health")
def health():
    return {
        "ok": True,
        "env": "hf",
        "port": os.getenv("PORT", "7860"),
        "graph_ready": app.state.graph is not None,
    }

@app.get("/healthz")
def healthz():
    return {"ok": True}

# ---------------- Routes ----------------
@app.post("/api/session/start")
def start(req: StartReq):
    sid = f"sess_{uuid.uuid4().hex[:8]}"
    state = OrchestratorState(
        session_id=sid,
        user_input=req.user_input,
        language=req.language,
        machine_area=req.area_hint,
        status="in_progress",
    )
    try:
        if getattr(app.state, "graph", None) is None:
            state.status = "degraded"
        else:
            state = _run_once(app.state.graph, state)
    except Exception:
        state.status = "error"
    SESSIONS[sid] = state
    return {"session_id": sid, "status": state.status}

@app.get("/api/session/status")
def status(session_id: str):
    st = SESSIONS.get(session_id)
    if not st:
        raise HTTPException(status_code=404, detail="not_found")
    return st.model_dump()

@app.post("/api/session/act")
def act(req: ActReq):
    st = SESSIONS.get(req.session_id)
    if not st:
        raise HTTPException(status_code=404, detail="not_found")

    action = req.action.lower().strip()
    if action == "confirm":
        dec = dict(st.decision or {})
        dec["pending_confirm"] = False
        dec["notify_supervisor"] = True
        st.decision = dec
        st.status = "in_progress"

        st = agents.report(st)
        st = agents.notify(st)

        st.status = "resolved"
        SESSIONS[st.session_id] = st
        return {"ok": True, "status": st.status}

    elif action == "escalate":
        st.status = "escalated"
        SESSIONS[st.session_id] = st
        return {"ok": True, "status": st.status}

    elif action == "stop":
        st.status = "resolved"
        SESSIONS[st.session_id] = st
        return {"ok": True, "status": st.status}

    else:
        raise HTTPException(status_code=400, detail="bad_action")

# ---- Scribe endpoints ----
@app.post("/api/scribe/event")
def scribe_event(ev: ScribeEventIn):
    try:
        append_event(ev.session_id, ev.role, ev.text)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, f"scribe_event error: {e}")

@app.post("/api/scribe/summarize")
def scribe_summarize(inp: ScribeSummIn, request: Request):
    try:
        url_path = build_and_save_report(inp.session_id)
        if isinstance(url_path, str) and url_path.startswith("/"):
            base = str(request.base_url).rstrip("/")
            return {"ok": True, "report_url": f"{base}{url_path}"}
        return {"ok": True, "report_url": url_path}
    except Exception as e:
        raise HTTPException(500, f"scribe_summarize error: {e}")

@app.post("/api/scribe/save_markdown")
def scribe_save_markdown(inp: ScribeSaveIn, request: Request):
    try:
        url_path = save_markdown_report(inp.session_id, inp.markdown)
        if isinstance(url_path, str) and url_path.startswith("/"):
            base = str(request.base_url).rstrip("/")
            return {"ok": True, "report_url": f"{base}{url_path}"}
        return {"ok": True, "report_url": url_path}
    except Exception as e:
        raise HTTPException(500, f"scribe_save_markdown error: {e}")

# ---- STT chunk endpoint ----
@app.post("/api/stt/chunk")
async def stt_chunk(session_id: str = Form(...), language: str | None = Form(None), file: UploadFile = File(...)):
    try:
        data = await file.read()
        text = stt_mod.transcribe_chunk(
            data,
            filename=(file.filename or "audio.webm"),
            mimetype=(file.content_type or "audio/webm"),
            language=language,
        )
        text = (text or "").strip()
        if text:
            append_event(session_id, "user", text)
        return {"text": text}
    except Exception as e:
        raise HTTPException(500, f"stt_chunk error: {e}")

# ---- STT placeholder ----
@app.post("/api/stt")
async def stt(file: UploadFile = File(...)):
    _ = await file.read()
    return {"text": "(transcription placeholder)"}

# ---- Simple WS demo ----
@app.websocket("/api/realtime/ws")
async def realtime_ws(ws: WebSocket):
    await ws.accept()
    await ws.send_json({"type": "hello", "msg": "socket alive"})
    try:
        while True:
            data = await ws.receive_text()
            txt = (data or "").strip()

            if txt.lower() == "ping":
                await ws.send_text("pong")
                continue

            if txt.lower().startswith("search:"):
                q = txt.split(":", 1)[1].strip()
                hits = web_search(q) or []
                await ws.send_json({"type": "search_results", "q": q, "results": hits})
                continue

            if txt.lower().startswith("say:"):
                user = txt.split(":", 1)[1].strip()
                md = chat_markdown(user)
                await ws.send_json({"type": "plan", "markdown": md})
                continue

            await ws.send_json({"type": "echo", "text": txt})
    except WebSocketDisconnect:
        return

# ---- Realtime ephemeral token ----
@app.post("/api/realtime/token")
def realtime_token(req: RealtimeTokenReq):
    api_key = os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL", "") or "https://api.openai.com"

    model = (req.model or os.getenv("REALTIME_MODEL", "gpt-4o-realtime-preview"))
    voice = (req.voice or "verse")

    if not api_key:
        raise HTTPException(status_code=500, detail="Missing OPENAI_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "realtime=v1",
    }
    payload = {"model": model, "voice": voice}

    try:
        url = f"{base_url.rstrip('/')}/v1/realtime/sessions"
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        client_secret = (data.get("client_secret") or {}).get("value")
        if not client_secret:
            raise RuntimeError("No client_secret returned")
        return {"client_secret": client_secret, "id": data.get("id"), "model": data.get("model")}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to mint ephemeral token: {e}")
