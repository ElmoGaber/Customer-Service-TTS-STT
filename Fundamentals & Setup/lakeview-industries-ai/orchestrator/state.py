from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class OrchestratorState(BaseModel):
    session_id: str
    language: Optional[str] = None
    machine_area: Optional[str] = None
    user_input: str

    proposed_steps: Optional[str] = None  # markdown string (BLUF, Steps, Checks, Safety)
    safety_notes: Optional[str] = None    # markdown string
    decision: Optional[Dict[str, Any]] = None

    kb_sources: List[Dict[str, str]] = Field(default_factory=list)
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    attempts: Dict[str, int] = Field(default_factory=dict)

    status: str = "in_progress"  # idle|in_progress|awaiting_confirm|resolved|escalated|error
    log_ref: Optional[str] = None
    error_info: Optional[str] = None

    assigned_agent: Optional[str] = None
