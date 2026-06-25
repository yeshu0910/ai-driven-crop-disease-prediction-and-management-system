# Memory storage wrapper tool for ADK
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

AGENT_MEMORY_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "agent_memory.json"
)


# ADK typed function
def save_farmer_history_tool(
    farmer_name: str,
    location: str,
    crop_name: str,
    disease_name: str,
    confidence: float,
    additional_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    from datetime import datetime

    record = {
        "farmer_name": farmer_name,
        "location": location,
        "crop_name": crop_name,
        "disease_name": disease_name,
        "confidence": confidence,
        "timestamp": datetime.now().isoformat(),
    }
    if additional_data:
        record.update(additional_data)

    existing = _load_memory()
    existing.append(record)
    _save_memory(existing)
    return {"success": True, "message": "History saved", "record": record}


# ADK typed function
def get_farmer_history_tool(
    farmer_name: Optional[str] = None, limit: int = 50
) -> List[Dict[str, Any]]:
    records = _load_memory()
    if farmer_name:
        records = [r for r in records if r.get("farmer_name") == farmer_name]
    return records[-limit:]


def _load_memory() -> List[Dict[str, Any]]:
    if AGENT_MEMORY_PATH.exists():
        with open(AGENT_MEMORY_PATH, "r") as f:
            return json.load(f)
    return []


def _save_memory(records: List[Dict[str, Any]]) -> None:
    AGENT_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AGENT_MEMORY_PATH, "w") as f:
        json.dump(records, f, indent=2)
