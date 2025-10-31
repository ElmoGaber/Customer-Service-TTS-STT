# orchestrator/graph_app.py
"""
Safe checkpoint loader for LangGraph on Hugging Face Spaces.
Avoids writing to /data root; uses subdirs and graceful fallbacks.
"""

import os
from pathlib import Path
from typing import Optional

try:
    from langgraph.checkpoint.sqlite import SqliteSaver
except Exception:
    SqliteSaver = None

from langgraph.checkpoint.memory import MemorySaver


def _mk_parent_dir(file_path: str):
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)


def get_checkpoint_saver(db_path: Optional[str] = None):
    """
    Try multiple writable locations for persistent SQLite.
    Fallback to MemorySaver if sqlite saver or paths fail.
    """
    if SqliteSaver is None:
        return MemorySaver()

    candidates = []

    # 1) If explicit override given: treat dir vs file
    if db_path:
        p = Path(db_path)
        if p.suffix.lower() != ".sqlite":
            p = p / "lv.sqlite"
        candidates.append(p)
    else:
        # 2) Env-provided dir (default to /data/checkpoints), not /data root
        base = os.environ.get("CHECKPOINT_DIR", "/data/checkpoints")
        candidates.append(Path(base) / "lv.sqlite")

    # 3) Fall back paths if permission denied
    candidates += [
        Path("/workspace/checkpoints/lv.sqlite"),
        Path("/tmp/checkpoints/lv.sqlite"),
    ]

    last_err = None
    for p in candidates:
        try:
            _mk_parent_dir(str(p))
            return SqliteSaver(str(p))
        except Exception as e:
            last_err = e
            continue

    # If all fail -> memory (non-persistent, but never crashes startup)
    return MemorySaver()


def build_graph():
    """
    Build and return your LangGraph compiled with a safe checkpointer.
    Replace the placeholder with your actual graph build.
    """
    db_override = os.environ.get("CHECKPOINT_DB")  # optional; can be dir or .sqlite path
    saver = get_checkpoint_saver(db_override)

    # TODO: replace with your real graph build, e.g.:
    # from langgraph.graph import StateGraph
    # from .schema import GraphState
    # graph = (
    #     StateGraph(GraphState)
    #     .add_nodes(...)
    #     .add_edges(...)
    #     .compile(checkpointer=saver)
    # )
    # return graph

    return saver  # placeholder to prevent crash if build not yet wired
