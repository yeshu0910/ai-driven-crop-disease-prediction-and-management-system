# Weather Agent - ADK Agent for weather and risk prediction
from typing import Any, Dict, Optional

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from ..tools.weather_tool import get_weather_tool, predict_disease_risk_tool


class WeatherAgent(Agent):
    def __init__(self, name: str = "weather_agent"):
        super().__init__(name=name)
        self.tools = [
            FunctionTool(get_weather_tool),
            FunctionTool(predict_disease_risk_tool),
        ]

    def get_current_weather(self, location: str) -> Dict[str, Any]:
        return get_weather_tool(location)

    def predict_risk(self, location: str, crop_name: str) -> Dict[str, Any]:
        return predict_disease_risk_tool(location, crop_name)

    def get_weather_with_risk(
        self, location: str, crop_name: Optional[str] = None
    ) -> Dict[str, Any]:
        weather = self.get_current_weather(location)
        risk = None
        if crop_name:
            risk = self.predict_risk(location, crop_name)
        return {"weather": weather, "risk": risk}
