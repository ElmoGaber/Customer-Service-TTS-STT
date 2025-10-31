from __future__ import annotations
from typing import List, Dict

def web_search(q: str) -> List[Dict[str,str]]:
    # Placeholder web search tool. Replace with a real search (and citation filtering).
    # Return: list of {title, url, snippet}
    return []

def read_plc(tag: str) -> str:
    # Placeholder PLC read. Connect to your PLC/SCADA and return a short string.
    return "unknown"

def fetch_order(order_id: str) -> dict:
    # Placeholder ERP call.
    return {"id": order_id, "status": "unknown"}
