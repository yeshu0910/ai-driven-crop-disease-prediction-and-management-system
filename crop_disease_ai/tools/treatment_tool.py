# Treatment recommendation wrapper tool for ADK
from typing import Any, Dict, Optional


# ADK typed function
def get_treatment_tool(
    crop_name: str,
    disease_name: str,
    severity: str,
    infection_percentage: float,
    weather_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    from utils.recommendation_engine import RecommendationEngine

    recommender = RecommendationEngine()
    return recommender.generate_recommendations(
        crop_name, disease_name, severity, infection_percentage, weather_data
    )
