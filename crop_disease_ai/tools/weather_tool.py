# Weather API wrapper tool for ADK
from typing import Any, Dict


# ADK typed function
def get_weather_tool(location: str) -> Dict[str, Any]:
    from utils.weather_api import WeatherAPI

    weather = WeatherAPI()
    return weather.get_current_weather(location)


# ADK typed function
def predict_disease_risk_tool(location: str, crop_name: str) -> Dict[str, Any]:
    from utils.weather_api import WeatherAPI

    weather = WeatherAPI()
    weather_data = weather.get_current_weather(location)
    return weather.get_disease_risk_from_weather(weather_data, crop_name)
