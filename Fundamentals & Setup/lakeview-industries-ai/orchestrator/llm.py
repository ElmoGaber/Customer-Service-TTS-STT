from __future__ import annotations
from typing import Optional

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore

from orchestrator.config import load_env

SETTINGS = load_env()

_client = None


def _client_ok() -> Optional[object]:
    global _client
    if _client is None and OpenAI is not None:
        kwargs = {}
        if SETTINGS.OPENAI_BASE_URL:
            kwargs["base_url"] = SETTINGS.OPENAI_BASE_URL
        _client = OpenAI(api_key=SETTINGS.OPENAI_API_KEY, **kwargs)
    return _client


def chat_markdown(user_prompt: str) -> str:
    """
    General-purpose chat → markdown helper used by SME/safety.
    NOTE: Honors DEV_OFFLINE for deterministic local testing.
    """
    import os
    if os.getenv("DEV_OFFLINE", "0") == "1":
        return (
            "BLUF: Reduce line speed slightly, retension, and inspect edge guides.\n\n"
            "## Steps\n"
            "1. Verify PPE and guards; LOTO if removing any guarding.\n"
            "2. Drop speed 30→25 and retension 100/90 to OEM spec.\n"
            "3. Inspect edge guides and knife sharpness; clean debris.\n"
            "4. Check material lot change and splice quality.\n"
            "5. Run 10m trial; watch fray and noise.\n"
            "6. Record settings and outcome.\n\n"
            "## Checks\n"
            "1. Fray reduced within 10m.\n"
            "2. Noise normal; no chatter.\n"
            "3. Tension stable ±5.\n\n"
            "## Safety\n"
            "1. PPE (gloves/eye/hearing). LOTO before blade/guard work.\n"
            "2. Respect tension/pressure limits.\n"
            "3. Stop if abnormal vibration.\n\n"
            "## If no improvement\n"
            "1. Swap to verified sharp knives.\n"
            "2. Escalate to maintenance for alignment.\n"
        )

    c = _client_ok()
    if not c:
        return (
            "BLUF: (offline) Provide a concise summary.\n\n"
            "## Steps\n1. Step A\n2. Step B\n\n"
            "## Checks\n1. Check X\n\n"
            "## Safety\n1. PPE\n\n"
            "## If no improvement\n1. Escalate"
        )
    try:
        resp = c.chat.completions.create(
            model=SETTINGS.CHAT_MODEL,
            messages=[
                {"role": "system", "content": "Return compact, useful markdown only. No chit-chat."},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return resp.choices[0].message.content or ""
    except Exception:
        return (
            "BLUF: (fallback) Reduce speed, retension, and inspect guides.\n\n"
            "## Steps\n1. PPE & guards.\n2. Speed 30→25; retension 100/90.\n3. Inspect guides/knives.\n"
            "4. Check lot/splice.\n5. 10m trial.\n6. Log result.\n\n"
            "## Checks\n1. Fray down.\n2. Noise normal.\n3. Tension stable.\n\n"
            "## Safety\n1. PPE & LOTO.\n\n"
            "## If no improvement\n1. Knife swap.\n2. Escalate."
        )


# ------------------ Scribe-specialized helpers (ALWAYS online if possible) ------------------

def chat_markdown_live(system: str, user: str, temperature: float = 0.2, max_tokens: int = 600) -> str:
    """
    A stricter helper for the scribe: bypasses DEV_OFFLINE and tries to hit the API.
    Falls back to a minimal placeholder if the API is unavailable.
    """
    c = _client_ok()
    if not c:
        return "(LLM unavailable)"
    try:
        resp = c.chat.completions.create(
            model=SETTINGS.CHAT_MODEL,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""
    except Exception:
        return "(LLM error)"


def summarize_problem(transcript_text: str) -> str:
    """
    Summarize a raw transcript into STRICT JSON with keys:
    BLUF (string), Problem (list), Proposed Steps (list), Checks (list), Safety (list).
    """
    import json, re

    system = (
        "You are IronPath's factory-floor scribe. Summarize the conversation.\n"
        "Use ONLY facts in the transcript. Be concise. No generic advice.\n"
        "Return STRICT JSON with keys exactly: "
        '["BLUF","Problem","Proposed Steps","Checks","Safety"]. '
        "BLUF is a single short sentence. Each list has 0–6 short items. No extra text."
    )
    user = (
        "Transcript (chronological, each line 'role: text'):\n"
        f"{transcript_text}\n\n"
        "Return JSON only."
    )
    raw = chat_markdown_live(system, user, temperature=0.0, max_tokens=700).strip()

    # Best-effort coercion to strict JSON (handles accidental code fences or pre/post text)
    candidate = raw
    m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if m:
        candidate = m.group(0)

    try:
        obj = json.loads(candidate)
    except Exception:
        # If parsing fails, return the model output as-is (caller can decide next step)
        return raw

    # Enforce required keys and types
    KEYS = ["BLUF", "Problem", "Proposed Steps", "Checks", "Safety"]
    norm = {}

    def _as_list(v):
        if v is None:
            return []
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()][:6]
        # if a single string came back, split bullets/lines
        if isinstance(v, str):
            parts = [p.strip(" -•\t") for p in re.split(r"[\n;]+", v) if p.strip()]
            return parts[:6]
        return []

    for k in KEYS:
        if k == "BLUF":
            v = obj.get(k) or obj.get(k.lower()) or ""
            norm[k] = (str(v).strip() if isinstance(v, str) else "")
        else:
            v = (
                obj.get(k)
                or obj.get(k.lower())
                or obj.get(k.replace(" ", ""))
                or obj.get(k.replace(" ", "_").lower())
            )
            norm[k] = _as_list(v)

    # Final strict JSON string
    try:
        return json.dumps(norm, ensure_ascii=False, separators=(",", ":"))
    except Exception:
        # Fallback to original raw if dumping somehow fails
        return raw


def summarize_incremental(previous_markdown: str, new_chunk_text: str) -> str:
    """
    Update an existing summary with a new chunk. Used for streaming workflows.
    """
    system = (
        "You update an existing troubleshooting summary. Keep it concise and structured. "
        "Only change sections affected by new information. Output markdown only."
    )
    user = (
        f"Current summary:\n{previous_markdown}\n\n"
        f"New transcript chunk:\n{new_chunk_text}\n"
        "Return the updated markdown with the same sections."
    )
    md = chat_markdown_live(system, user, temperature=0.2, max_tokens=700)
    return md.strip() or previous_markdown
