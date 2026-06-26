# Memory Agent - ADK Agent for farmer history storage
from typing import Any, Dict, List, Optional

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from ..memory.farmer_memory import FarmerMemory
from ..tools.memory_tool import get_farmer_history_tool, save_farmer_history_tool


class MemoryAgent(Agent):
    def __init__(self, name: str = "memory_agent"):
        super().__init__(name=name)
        self.tools = [
            FunctionTool(save_farmer_history_tool),
            FunctionTool(get_farmer_history_tool),
        ]
        self.memory = FarmerMemory()

    def save_to_memory(
        self,
        farmer_name: str,
        location: str,
        crop_name: str,
        disease_name: str,
        confidence: float,
        **kwargs,
    ) -> Dict[str, Any]:
        return save_farmer_history_tool(
            farmer_name, location, crop_name, disease_name, confidence, kwargs
        )

    def get_history(
        self, farmer_name: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        return self.memory.get_history(farmer_name, limit)

    def get_statistics(self, farmer_name: Optional[str] = None) -> Dict[str, Any]:
        return self.memory.get_statistics(farmer_name)
