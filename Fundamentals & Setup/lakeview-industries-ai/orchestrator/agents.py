from __future__ import annotations
import os

from typing import List
import datetime

from orchestrator.state import OrchestratorState
from orchestrator.llm import chat_markdown
from orchestrator.tools import web_search
from orchestrator.storage_s3 import save_html_report
from orchestrator.notify_email import notify_supervisor

STYLE = {
    "header": "# BLUF\n{bluf}\n\n## Steps\n{steps}\n\n## Checks\n{checks}\n\n## Safety\n{safety}\n\n## If no improvement\n{fallbacks}\n",
    "sme": (
        "Role: Senior {area} technician.\n"
        "Style: 1-line BLUF, ≤6 numbered steps, ≤3 checks, ≤2 fallbacks. No chit-chat.\n"
        "If missing info, ask ≤3 precise questions at the end.\n"
        "Return markdown only.\n"
        "Input: {user_input}\n"
        "{web_note}\n"
    ),
    "safety": (
        "Role: Safety/QA.\n"
        "Add mandatory PPE/LOTO/limits. If risk unclear or model not confident, return 'Stop & Escalate' with 1 reason.\n"
        "Preserve BLUF/Steps/Checks succinctly.\n"
        "Input markdown:\n{draft}\n"
    ),
    "decision": (
        "Role: Operations lead.\n"
        "Decide route based on the plan quality and risk. Priorities: safety > clarity > speed.\n"
        "Return strictly one of:\n"
        "- needs_more_info: yes/no\n"
        "- escalate: yes/no\n"
        "- create_doc: yes/no\n"
        "- notify_supervisor: yes/no\n"
        "Use yes for at most one of create_doc/notify_supervisor; if create_doc=yes, notify_supervisor should be no.\n"
        "Context:\n{draft}\n"
    ),
}
# --- normalize_markdown (safe no-op formatter) -------------------------------
# --- normalize_markdown (safe no-op) -----------------------------------------
def normalize_markdown(md: str) -> str:
    """
    Ensure the output has the expected sections and trim whitespace.
    If empty, return a minimal scaffold so downstream code never crashes.
    """
    md = (md or "").strip()
    if not md:
        return (
            "# BLUF\n(none)\n\n"
            "## Steps\n- (none)\n\n"
            "## Checks\n- (none)\n\n"
            "## Safety\n- (none)\n\n"
            "## If no improvement\n- (none)\n"
        )
    return md


def _mk_list(items: List[str], limit: int) -> str:
    items = [s.strip() for s in items if s and s.strip()]
    items = items[:limit] if limit else items
    if not items:
        return "- (none)"
    out = []
    for i, s in enumerate(items, 1):
        out.append(f"{i}. {s}")
    return "\n".join(out)

def intake_router(state: OrchestratorState) -> OrchestratorState:
    txt = (state.user_input or "").lower()
    area = state.machine_area or ("slitter" if "slit" in txt else "laminator" if "lamin" in txt else "general")
    state.machine_area = area
    state.assigned_agent = "intake_router"
    return state

def sme(state: OrchestratorState) -> OrchestratorState:
    area = state.machine_area or "general"
    web_note = ""
    hints = web_search(f"{area} troubleshooting checklist") or []
    if hints:
        web_note = "Web summaries available."
    prompt = STYLE["sme"].format(area=area, user_input=state.user_input, web_note=web_note)
    draft = chat_markdown(prompt)
    state.proposed_steps = draft
    state.assigned_agent = "sme"
    return state

def safety(state: OrchestratorState) -> OrchestratorState:
    draft = state.proposed_steps or ""
    prompt = STYLE["safety"].format(draft=draft)
    safer = chat_markdown(prompt)
    state.safety_notes = safer
    state.proposed_steps = safer
    state.assigned_agent = "safety"
    return state

def decision(state: OrchestratorState) -> OrchestratorState:
    draft = state.proposed_steps or ""
    prompt = STYLE["decision"].format(draft=draft)
    text = chat_markdown(prompt)

    flags = {k: False for k in ("needs_more_info", "escalate", "create_doc", "notify_supervisor")}
    for line in text.splitlines():
        parts = [p.strip().lower() for p in line.split(":")]
        if len(parts) == 2 and parts[0] in flags:
            flags[parts[0]] = parts[1].startswith("y")

    # Dev override to exercise confirm/report path
    if os.getenv("DEV_FORCE_CREATE_DOC", "0") == "1":
        flags["create_doc"] = True
        flags["notify_supervisor"] = False

    state.decision = flags
    state.assigned_agent = "decision"
    return state

def report(state: OrchestratorState) -> OrchestratorState:
    html = f"""<html><head><meta charset='utf-8'><title>IronPath {state.session_id}</title></head>
<body style='font-family: ui-sans-serif, system-ui; max-width: 800px; margin: 40px auto;'>
<h2>Session {state.session_id} — {state.machine_area or ''}</h2>
<pre style='white-space: pre-wrap'>{state.proposed_steps or ''}</pre>
<hr>
<small>Generated {datetime.datetime.utcnow().isoformat()}Z</small>
</body></html>"""
    ref = save_html_report(state.session_id, html)
    state.log_ref = ref
    state.assigned_agent = "report"
    return state

def notify(state: OrchestratorState) -> OrchestratorState:
    notify_supervisor(state)
    state.assigned_agent = "notify"
    state.status = "resolved"

    return state
