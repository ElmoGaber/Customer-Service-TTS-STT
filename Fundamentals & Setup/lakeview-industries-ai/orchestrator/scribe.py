from __future__ import annotations
import json, datetime, pathlib, re
from typing import List, Dict

from orchestrator.llm import summarize_problem
from orchestrator.storage_s3 import save_html_report

# Absolute sessions dir resolved by server mount; keep JSONL here
SESS_DIR = pathlib.Path("sessions")
SESS_DIR.mkdir(parents=True, exist_ok=True)


def _path(session_id: str) -> pathlib.Path:
    return SESS_DIR / f"{session_id}.jsonl"


def append_event(session_id: str, role: str, text: str):
    if not session_id or not role or not text:
        return
    rec = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "role": role,               # "user" | "assistant" | "system"
        "text": text.strip()
    }
    with _path(session_id).open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def read_transcript(session_id: str, limit_chars: int = 4000) -> List[Dict]:
    p = _path(session_id)
    if not p.exists():
        return []
    out: List[Dict] = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    # Keep last ~limit_chars to control token use
    total = 0
    trimmed: List[Dict] = []
    for rec in reversed(out):
        total += len(rec.get("text", ""))
        trimmed.append(rec)
        if total >= limit_chars:
            break
    return list(reversed(trimmed))


# ---------- local fallback if the LLM is unavailable ----------
def _fallback_local_summary(notes: List[Dict]) -> str:
    """Produce a concise markdown summary without calling an LLM."""
    # 1) Problem = last user line that looks like a problem statement
    problem_lines = []
    for r in reversed(notes):
        if r["role"] == "user":
            t = r["text"]
            if len(t) > 6:
                problem_lines = [t]
                break
    if not problem_lines:
        problem_lines = ["(not captured)"]

    # 2) Proposed steps = extract imperative-looking sentences from assistant
    steps = []
    for r in notes:
        if r["role"] != "assistant":
            continue
        # split on sentence-ish boundaries
        parts = re.split(r'(?<=[\.\!\?])\s+', r["text"])
        for s in parts:
            s = s.strip(" \n\r\t-*")
            if not s:
                continue
            # simple heuristic: starts with a verb/number/bullet
            if re.match(r'^(\d+\.|\-|\*)\s*', s) or re.match(r'^(check|verify|inspect|reduce|increase|retension|clean|swap|adjust|record|run|stop|escalate|replace|tighten|lubricate)\b', s.lower()):
                steps.append(s)
            # Keep it short
            if len(steps) >= 6:
                break
        if len(steps) >= 6:
            break
    if not steps:
        steps = ["(not captured)"]

    # 3) Checks: pick short assistant lines containing success criteria
    checks = []
    for r in notes:
        if r["role"] != "assistant":
            continue
        for s in re.split(r'(?<=[\.\!\?])\s+', r["text"]):
            s = s.strip()
            if not s:
                continue
            if any(k in s.lower() for k in ["should", "within", "no ", "stable", "target", "spec"]):
                checks.append(s)
            if len(checks) >= 3:
                break
        if len(checks) >= 3:
            break
    if not checks:
        checks = ["(none)"]

    # 4) Safety: look for PPE/LOTO keywords
    safety = []
    for r in notes:
        if r["role"] != "assistant":
            continue
        t = r["text"].lower()
        if any(k in t for k in ["ppe", "loto", "lockout", "guard", "blade", "pressure limit", "voltage", "hazard"]):
            for s in re.split(r'(?<=[\.\!\?])\s+', r["text"]):
                if any(k in s.lower() for k in ["ppe", "loto", "lockout", "guard", "blade", "pressure", "voltage", "hazard"]):
                    safety.append(s.strip())
        if len(safety) >= 3:
            break
    if not safety:
        safety = ["(none)"]

    # BLUF: compress problem to one line
    bluf = problem_lines[0]
    if len(bluf) > 120:
        bluf = bluf[:117] + "…"

    def bullets(arr): return "\n".join(f"- {x}" for x in arr)

    return (
        f"# BLUF\n{bluf}\n\n"
        f"## Problem\n{bullets(problem_lines)}\n\n"
        f"## Proposed Steps\n{bullets(steps)}\n\n"
        f"## Checks\n{bullets(checks)}\n\n"
        f"## Safety\n{bullets(safety)}\n"
    )


def summarize_to_markdown(session_id: str) -> str:
    notes = read_transcript(session_id)
    if not notes:
        return "# BLUF\n(no conversation captured)\n"
    convo = "\n".join([f"{r['role']}: {r['text']}" for r in notes])

    # Try LLM
    md = summarize_problem(convo).strip()
    # If the LLM failed or returned an error string, fall back locally
    if not md or md.lower().startswith("(llm"):
        md = _fallback_local_summary(notes)
    return md


# ---------- NEW: tiny normalizer for summaries ----------

def _dedupe_list(xs):
    seen = set()
    out = []
    for x in xs or []:
        s = str(x).strip()
        if not s:
            continue
        # normalize spaces & trailing periods for better dedupe
        s2 = " ".join(s.split()).rstrip(".")
        if s2.lower() in seen:
            continue
        seen.add(s2.lower())
        out.append(s2 if s.endswith(".") else s2)  # we’ll add bullets without extra periods
    return out


def _normalize_summary(md_or_json: str) -> str:
    """
    Accepts raw text from Realtime (possibly duplicate/JSON-ish) and returns
    clean, compact Markdown with sections: BLUF, Problem, Proposed Steps, Checks, Safety.
    """
    text = (md_or_json or "").strip()

    # 1) Try to parse JSON if it looks like it
    def try_json(s: str):
        try:
            return json.loads(s)
        except Exception:
            # handle escaped JSON inside quotes
            try:
                return json.loads(s.strip('`"'))
            except Exception:
                return None

    j = try_json(text)

    # JSON branch (dedupe + bulletize)
    if isinstance(j, dict) and any(k.lower() in j for k in ("bluf", "problem", "proposed steps", "checks", "safety")):
        bluf = (j.get("BLUF") or j.get("bluf") or "").strip()
        prob  = _dedupe_list(j.get("Problem") or j.get("problem") or [])
        steps = _dedupe_list(j.get("Proposed Steps") or j.get("proposed_steps") or [])
        checks= _dedupe_list(j.get("Checks") or j.get("checks") or [])
        safety= _dedupe_list(j.get("Safety") or j.get("safety") or [])

        def bullets(x): return "\n".join(f"- {i}" for i in x) if x else "- (none)"
        return (
            f"# BLUF\n{bluf or '(none)'}\n\n"
            f"## Problem\n{bullets(prob)}\n\n"
            f"## Proposed Steps\n{bullets(steps)}\n\n"
            f"## Checks\n{bullets(checks)}\n\n"
            f"## Safety\n{bullets(safety)}\n"
        )

    # 2) If not JSON: collapse repeated blocks and whitespace
    # Keep last occurrence of each section-like header
    # Simple de-dup: split on repeated 'BLUF'/'Problem' etc and take the last chunk
    lowers = text.lower()
    for key in ["bluf", "problem", "proposed steps", "checks", "safety"]:
        idx = lowers.rfind(key)
        if idx > 0:
            text = text[idx-2:]  # keep from last section heading
            break

    # 3) Ensure markdown headers exist; if not, wrap as BLUF-only
    if not re.search(r"(?mi)^\s*#\s*bluf\b", text):
        text = f"# BLUF\n{text.strip()}\n"

    # 4) Make headers consistent
    text = re.sub(r"(?mi)^\s*bluf\s*[:\-]\s*", "# BLUF\n", text)
    text = re.sub(r"(?mi)^\s*#\s*bluf\b.*", "# BLUF", text)
    mapping = {
        r"(?mi)^\s*(problem|#\s*problem)\b.*": "## Problem",
        r"(?mi)^\s*(proposed steps|steps|#\s*steps)\b.*": "## Proposed Steps",
        r"(?mi)^\s*(checks|#\s*checks)\b.*": "## Checks",
        r"(?mi)^\s*(safety|#\s*safety)\b.*": "## Safety",
    }
    for pat, repl in mapping.items():
        text = re.sub(pat, repl, text)

    # 5) Squeeze excessive spaces
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text or "# BLUF\n(none)\n"


# ---------- NEW: save a report directly from provided markdown ----------
def save_markdown_report(session_id: str, markdown: str) -> str:
    md = _normalize_summary(markdown)
    html = f"""<html><head><meta charset="utf-8">
<title>IronPath Report — {session_id}</title>
<style>
body{{font-family:ui-sans-serif,system-ui;max-width:820px;margin:40px auto;line-height:1.45}}
pre{{white-space:pre-wrap;background:#f7f7f7;padding:12px;border-radius:8px}}
h2{{margin-bottom:.25rem}}
small{{color:#666}}
</style></head><body>
<h2>IronPath Session Report</h2>
<p><b>Session:</b> {session_id}</p>
<pre>{md}</pre>
<small>Generated {__import__('datetime').datetime.utcnow().isoformat()}Z</small>
</body></html>"""
    from orchestrator.storage_s3 import save_html_report
    return save_html_report(session_id, html)


def build_and_save_report(session_id: str) -> str:
    md = summarize_to_markdown(session_id)
    html = f"""<html><head><meta charset="utf-8">
<title>IronPath Report — {session_id}</title>
<style>
body{{font-family:ui-sans-serif,system-ui;max-width:820px;margin:40px auto;line-height:1.45}}
pre{{white-space:pre-wrap;background:#f7f7f7;padding:12px;border-radius:8px}}
h2{{margin-bottom:.25rem}}
small{{color:#666}}
</style>
</head><body>
<h2>IronPath Session Report</h2>
<p><b>Session:</b> {session_id}</p>
<pre>{md}</pre>
<small>Generated {datetime.datetime.utcnow().isoformat()}Z</small>
</body></html>"""
    return save_html_report(session_id, html)
