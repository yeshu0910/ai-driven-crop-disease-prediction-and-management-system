# Treatment Agent - ADK Agent for treatment recommendations
from typing import Any, Dict, Optional

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from ..tools.treatment_tool import get_treatment_tool


class TreatmentAgent(Agent):
    def __init__(self, name: str = "treatment_agent"):
        super().__init__(name=name)
        self.tools = [FunctionTool(get_treatment_tool)]

    def recommend(
        self,
        disease_result: Dict[str, Any],
        weather_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        crop_name = disease_result.get("crop_name", "Unknown")
        disease_name = disease_result.get("disease_name", "Unknown")
        severity = "Mild"  # Default severity
        infection_pct = 50.0  # Default estimate
        if (
            "severity" in str(disease_name).lower()
            or "healthy" not in disease_name.lower()
        ):
            infection_pct = 75.0
        return get_treatment_tool(
            crop_name, disease_name, severity, infection_pct, weather_data
        )

    def get_chemical_treatment(self, disease_result: Dict[str, Any]) -> list:
        recommendations = self.recommend(disease_result)
        return recommendations.get("chemical_treatment", [])

    def get_organic_treatment(self, disease_result: Dict[str, Any]) -> list:
        recommendations = self.recommend(disease_result)
        return recommendations.get("organic_treatment", [])
