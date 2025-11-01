# core/llm_router.py
from utils.logger import setup_logger
from core.qwen_wrapper import call_qwen
from core.mistral_wrapper import call_mistral
import json
import os
from configs.settings import COMMAND_CONFIDENCE_THRESHOLD

logger = setup_logger()

def is_command_like(text: str) -> bool:
    """
    Very simple heuristic — replace with proper intent classifier in production.
    """
    commands_keywords = ["open", "play", "search", "calculate", "compute", "send", "call", "email", "search for", "افتح", "شغل", "ابحث"]
    txt = text.lower()
    return any(k in txt for k in commands_keywords)

def route_text(text: str, context: list = None):
    """
    Decide which LLM to call and return unified response object.
    """
    logger.info("Routing text: %s", text[:120])
    try:
        if is_command_like(text):
            logger.info("Detected as command-like -> Qwen")
            q = call_qwen(text)
            if q.get("type") == "tool" or q.get("confidence", 0) >= COMMAND_CONFIDENCE_THRESHOLD:
                return q
            # else fallback to mistral
            logger.info("Qwen low-confidence or tool not used, fallback to Mistral")
            return call_mistral(text, context)
        else:
            # conversational -> Mistral normally
            return call_mistral(text, context)
    except Exception as e:
        logger.exception("Router error: %s", e)
        # final safe fallback to qwen
        return call_qwen(text)
