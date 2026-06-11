import numpy as np
from utils.config import SEVERITY_LEVELS


class SeverityAnalyzer:
    def __init__(self):
        self.levels = SEVERITY_LEVELS

    def analyze(self, infection_percentage, disease_name, confidence):
        is_healthy = "healthy" in disease_name.lower()

        if is_healthy:
            severity = "Healthy"
            risk_level = "None"
        elif infection_percentage < 10:
            severity = "Mild"
            risk_level = "Low"
        elif infection_percentage < 30:
            severity = "Moderate"
            risk_level = "Medium"
        else:
            severity = "Severe"
            risk_level = "High"

        spread_estimation = self._estimate_spread(severity, disease_name)

        return {
            "severity": severity,
            "infection_percentage": round(infection_percentage, 2),
            "risk_level": risk_level,
            "spread_estimation": spread_estimation,
            "color": self.levels[severity]["color"],
            "icon": self.levels[severity]["icon"]
        }

    def _estimate_spread(self, severity, disease_name):
        estimates = {
            "Mild": "Disease detected in early stage. Spread potential is low with proper treatment.",
            "Moderate": "Disease is actively developing. Moderate spread expected within 1-2 weeks without intervention.",
            "Severe": "Advanced disease stage. Rapid spread to neighboring plants expected. Immediate action required.",
            "Healthy": "No disease detected. Continue preventive measures."
        }
        return estimates.get(severity, "Unable to estimate spread.")

    def get_severity_meter_value(self, severity):
        mapping = {"Healthy": 0, "Mild": 25, "Moderate": 55, "Severe": 90}
        return mapping.get(severity, 0)

    def get_treatment_urgency(self, severity):
        urgency_map = {
            "Healthy": "No treatment needed",
            "Mild": "Low urgency - treat within 7 days",
            "Moderate": "Medium urgency - treat within 3-4 days",
            "Severe": "High urgency - treat immediately"
        }
        return urgency_map.get(severity, "Unknown")

    def get_severity_description(self, severity):
        descriptions = {
            "Healthy": "The crop appears healthy with no signs of disease infection.",
            "Mild": "Early stage infection detected. Minor symptoms visible. Disease can be controlled with timely intervention.",
            "Moderate": "Active disease progression. Clear symptoms visible across plant tissue. Requires prompt treatment to prevent yield loss.",
            "Severe": "Advanced infection stage. Extensive tissue damage observed. Immediate intensive treatment needed to save the crop."
        }
        return descriptions.get(severity, "Unable to determine severity description.")

    def calculate_yield_impact(self, severity, crop_type):
        base_yield_impacts = {
            "Healthy": 0,
            "Mild": 5,
            "Moderate": 15,
            "Severe": 35
        }
        base = base_yield_impacts.get(severity, 0)

        crop_sensitivity = {
            "Tomato": 1.2, "Potato": 1.3, "Rice": 1.1, "Wheat": 1.0,
            "Corn": 0.9, "Cotton": 1.0, "Soybean": 0.8, "Sugarcane": 0.7,
            "Groundnut": 0.9, "Sunflower": 0.8, "Banana": 1.1, "Mango": 0.9,
            "Grapes": 1.3, "Apple": 1.2, "Chili": 1.0
        }
        sensitivity = crop_sensitivity.get(crop_type, 1.0)
        impact = min(base * sensitivity, 80)
        return round(impact, 1)
