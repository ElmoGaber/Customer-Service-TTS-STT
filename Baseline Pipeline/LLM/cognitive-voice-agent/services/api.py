# services/api.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn
import os
import uuid
from utils.logger import setup_logger
from core.stt_runner import smoke_test as stt_smoke  # can be direct run_whisper_cli
from core.tts_runner import load_tts, tts_generate_bytes, tts_generate_to_file
from core.llm_router import route_text
from configs.settings import AUDIO_OUT, METRICS_OUT, API_HOST, API_PORT

logger = setup_logger()
app = FastAPI(title="Cognitive Voice Agent API")

# Load TTS once on startup
TTS_MODEL = None
@app.on_event("startup")
def startup_event():
    global TTS_MODEL
    try:
        TTS_MODEL = load_tts()
        logger.info("TTS loaded on startup")
    except Exception as e:
        logger.exception("Failed to load TTS on startup: %s", e)

@app.post("/process")
async def process_audio_or_text(
    audio: UploadFile = File(None),
    text: str = Form(None),
    language: str = Form("auto"),
    speaker: str = Form(None)
):
    """
    If audio is provided -> run STT then LLM -> TTS
    If text provided -> only LLM -> TTS
    Returns JSON with path to WAV file and metadata.
    """
    session_id = str(uuid.uuid4())
    logger.info("Session %s - received request audio=%s text=%s", session_id, bool(audio), bool(text))

    if audio:
        # save uploaded audio to temporary path
        tmp_path = os.path.join(AUDIO_OUT, f"input_{session_id}.wav")
        os.makedirs(AUDIO_OUT, exist_ok=True)
        with open(tmp_path, "wb") as f:
            f.write(await audio.read())
        # run local STT
        stt_result = stt_smoke(tmp_path, save_metrics=True)
        user_text = stt_result.get("transcript", "")
        stt_meta = stt_result
    elif text:
        user_text = text
        stt_meta = None
    else:
        return JSONResponse({"error": "No audio or text provided"}, status_code=400)

    # route to LLMs
    llm_response = route_text(user_text, context=None)
    # unify text to speak
    speak_text = llm_response.get("text", "")
    # generate TTS (file)
    tts_metrics = tts_generate_to_file(TTS_MODEL, speak_text, speaker=speaker, language=language)
    # return output path and metadata
    out = {
        "session_id": session_id,
        "input_text": user_text,
        "llm_response": llm_response,
        "tts": tts_metrics,
        "stt": stt_meta
    }
    # save summary
    os.makedirs(METRICS_OUT, exist_ok=True)
    from utils.json_utils import save_json
    save_json(os.path.join(METRICS_OUT, f"session_{session_id}.json"), out)
    return out

@app.get("/stream/{file_name}")
def stream_file(file_name: str):
    # security: sanitize path in prod
    path = os.path.join(AUDIO_OUT, file_name)
    if not os.path.exists(path):
        return JSONResponse({"error": "file not found"}, status_code=404)
    def iterfile():
        with open(path, "rb") as f:
            chunk = f.read(4096)
            while chunk:
                yield chunk
                chunk = f.read(4096)
    return StreamingResponse(iterfile(), media_type="audio/wav")

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
