# Farmer memory storage class
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

AGENT_MEMORY_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "agent_memory.json"
)


class FarmerMemory:
    def __init__(self):
        self._ensure_storage_dir()

    def _ensure_storage_dir(self) -> None:
        AGENT_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> List[Dict[str, Any]]:
        if AGENT_MEMORY_PATH.exists():
            with open(AGENT_MEMORY_PATH, "r") as f:
                return json.load(f)
        return []

    def _save(self, records: List[Dict[str, Any]]) -> None:
        with open(AGENT_MEMORY_PATH, "w") as f:
            json.dump(records, f, indent=2)

    def add_record(
        self,
        farmer_name: str,
        location: str,
        crop_name: str,
        disease_name: str,
        confidence: float,
        **kwargs,
    ) -> None:
        record = {
            "farmer_name": farmer_name,
            "location": location,
            "crop_name": crop_name,
            "disease_name": disease_name,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
        }
        record.update(kwargs)
        records = self._load()
        records.append(record)
        self._save(records)

    def get_history(
        self, farmer_name: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        records = self._load()
        if farmer_name:
            records = [r for r in records if r.get("farmer_name") == farmer_name]
        return records[-limit:]

    def get_statistics(self, farmer_name: Optional[str] = None) -> Dict[str, Any]:
        records = self.get_history(farmer_name)
        if not records:
            return {"total_scans": 0, "diseases_found": 0, "healthy_scans": 0}
        diseases = sum(
            1 for r in records if "healthy" not in r.get("disease_name", "").lower()
        )
        healthy = sum(
            1 for r in records if "healthy" in r.get("disease_name", "").lower()
        )
        return {
            "total_scans": len(records),
            "diseases_found": diseases,
            "healthy_scans": healthy,
        }
