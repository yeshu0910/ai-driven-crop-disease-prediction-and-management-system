# Conversation history storage for agents
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

CONVERSATION_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "conversations.json"
)


class ConversationHistory:
    def __init__(self):
        self._ensure_storage_dir()

    def _ensure_storage_dir(self) -> None:
        CONVERSATION_PATH.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> List[Dict[str, Any]]:
        if CONVERSATION_PATH.exists():
            with open(CONVERSATION_PATH, "r") as f:
                return json.load(f)
        return []

    def _save(self, records: List[Dict[str, Any]]) -> None:
        with open(CONVERSATION_PATH, "w") as f:
            json.dump(records, f, indent=2)

    def add_message(self, agent_name: str, role: str, content: str, **metadata) -> None:
        record = {
            "agent": agent_name,
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        record.update(metadata)
        records = self._load()
        records.append(record)
        self._save(records)

    def get_conversation(
        self, agent_name: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        records = self._load()
        if agent_name:
            records = [r for r in records if r.get("agent") == agent_name]
        return records[-limit:]
