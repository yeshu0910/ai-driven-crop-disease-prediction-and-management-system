# Disease Agent - ADK Agent for disease prediction
from typing import Any, Dict, Optional

import numpy as np
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from ..memory.farmer_memory import FarmerMemory
from ..tools.disease_tool import predict_disease_tool


class DiseaseAgent(Agent):
    def __init__(self, name: str = "disease_agent"):
        super().__init__(name=name)
        self.tools = [FunctionTool(predict_disease_tool)]
        self.memory = FarmerMemory()

    def predict(
        self, image_array: np.ndarray, crop_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        result = predict_disease_tool(image_array, crop_hint)
        return result

    def predict_and_store(
        self,
        image_array: np.ndarray,
        farmer_name: str,
        location: str,
        crop_hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        result = self.predict(image_array, crop_hint)
        if result.get("success"):
            self.memory.add_record(
                farmer_name=farmer_name,
                location=location,
                crop_name=result.get("crop_name", "Unknown"),
                disease_name=result.get("disease_name", "Unknown"),
                confidence=result.get("confidence", 0.0),
            )
        return result
