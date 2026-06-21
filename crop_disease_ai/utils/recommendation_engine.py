from utils.disease_knowledge_base import DiseaseKnowledgeBase


class RecommendationEngine:
    def __init__(self):
        self.knowledge_base = DiseaseKnowledgeBase()

    def generate_recommendations(
        self, crop_name, disease_name, severity, infection_percentage, weather_data=None
    ):
        is_healthy = "healthy" in disease_name.lower()

        if is_healthy:
            return self._healthy_recommendations(crop_name, weather_data)

        disease_info = self.knowledge_base.get_disease_info(disease_name)

        chemical = self._get_chemical_treatment(disease_info, severity, crop_name)
        organic = self._get_organic_treatment(disease_info, severity, crop_name)
        fertilizers = self._get_fertilizer_suggestions(
            crop_name, disease_name, severity
        )
        irrigation = self._get_irrigation_guidance(
            crop_name, disease_name, severity, weather_data
        )
        prevention = self._get_prevention_measures(disease_info, severity, weather_data)
        management = self._get_crop_management_tips(
            crop_name, disease_name, severity, weather_data
        )

        return {
            "chemical_treatment": chemical,
            "organic_treatment": organic,
            "fertilizer_suggestions": fertilizers,
            "irrigation_guidance": irrigation,
            "prevention_measures": prevention,
            "crop_management_tips": management,
            "urgency": self._get_urgency(severity),
        }

    def _healthy_recommendations(self, crop_name, weather_data):
        return {
            "chemical_treatment": [
                "No chemical treatment needed - crop appears healthy",
                "Continue preventive fungicide schedule if in high-risk season",
                "Monitor for pest populations regularly",
            ],
            "organic_treatment": [
                "Continue organic farming practices",
                "Apply compost tea as a preventive health booster",
                "Maintain beneficial insect populations",
            ],
            "fertilizer_suggestions": [
                f"Apply balanced NPK fertilizer as per {crop_name} growth stage",
                "Consider foliar application of micronutrients",
                "Maintain soil organic matter with compost application",
            ],
            "irrigation_guidance": self._get_base_irrigation(crop_name, weather_data),
            "prevention_measures": [
                "Continue regular field scouting",
                "Maintain proper plant spacing for air circulation",
                "Practice good field sanitation",
                "Keep records of crop development",
            ],
            "crop_management_tips": [
                f"Maintain regular monitoring schedule for {crop_name}",
                "Document any unusual changes in plant appearance",
                "Plan for next preventive treatment cycle",
            ],
            "urgency": "No urgency - preventive maintenance",
        }

    def _get_chemical_treatment(self, disease_info, severity, crop_name):
        base_treatment = disease_info.get("treatment", [])
        if severity == "Mild":
            return base_treatment[:3] if len(base_treatment) >= 3 else base_treatment
        elif severity == "Moderate":
            return base_treatment[:5] if len(base_treatment) >= 5 else base_treatment
        else:
            full = list(base_treatment)
            full.append("Consider professional consultation for severe cases")
            full.append("Apply treatment immediately and repeat every 5-7 days")
            return full

    def _get_organic_treatment(self, disease_info, severity, crop_name):
        return disease_info.get(
            "organic_treatment",
            [
                "Apply neem oil spray (5ml/L water) weekly",
                "Use copper-based fungicides approved for organic farming",
                "Apply Bacillus subtilis-based biofungicide",
            ],
        )

    def _get_fertilizer_suggestions(self, crop_name, disease_name, severity):
        suggestions = []
        if severity in ["Moderate", "Severe"]:
            suggestions.extend(
                [
                    f"Reduce nitrogen application to {crop_name} - excess N increases disease susceptibility",
                    "Apply potassium-rich fertilizer to strengthen plant cell walls",
                    "Foliar spray of micronutrients (Zn, Mn, Cu) to boost immunity",
                    "Apply calcium to improve plant tissue strength",
                ]
            )
        else:
            suggestions.extend(
                [
                    f"Maintain balanced NPK fertilization for {crop_name}",
                    "Apply organic compost to improve soil health",
                    "Consider slow-release fertilizer formulations",
                ]
            )
        return suggestions

    def _get_irrigation_guidance(self, crop_name, disease_name, severity, weather_data):
        suggestions = []
        if severity in ["Moderate", "Severe"]:
            suggestions.extend(
                [
                    "Use drip irrigation instead of overhead sprinklers",
                    "Water at the base of plants to keep foliage dry",
                    "Water in the morning so foliage dries during the day",
                    "Reduce irrigation frequency slightly to avoid excess moisture",
                    "Ensure proper drainage around plants",
                ]
            )
        else:
            suggestions.extend(self._get_base_irrigation(crop_name, weather_data))

        if weather_data:
            humidity = weather_data.get("humidity", 50)
            if humidity > 75:
                suggestions.append("High humidity detected - reduce watering frequency")
            if weather_data.get("rainfall", 0) > 5:
                suggestions.append("Significant rainfall expected - skip irrigation")

        return suggestions

    def _get_base_irrigation(self, crop_name, weather_data):
        irrigation_guides = {
            "Tomato": "Water deeply 2-3 times per week; maintain consistent moisture. Avoid wetting foliage.",
            "Potato": "Keep soil consistently moist; provide 1-2 inches water weekly. Increase during tuber formation.",
            "Rice": "Maintain flooded conditions (2-5 cm water depth) during growing season.",
            "Wheat": "Water at critical stages: tillering, jointing, and grain filling. Provide 3-4 irrigations.",
            "Corn": "Water 1-1.5 inches weekly; critical during silking and grain fill.",
            "Cotton": "Water deeply but infrequently; reduce after boll opening.",
            "Soybean": "Provide 1 inch water weekly during flowering and pod fill.",
            "Sugarcane": "Maintain adequate moisture; irrigate every 7-10 days.",
            "Groundnut": "Water during peg formation and pod development; avoid overwatering.",
            "Sunflower": "Water at flowering and seed filling stages.",
            "Banana": "Provide 1-2 inches water weekly; keep soil consistently moist.",
            "Mango": "Water during flowering and fruit development; reduce during monsoon.",
            "Grapes": "Drip irrigation preferred; water during berry development.",
            "Apple": "Provide consistent moisture during fruit development.",
            "Chili": "Water regularly; maintain even moisture for fruit development.",
        }
        base = irrigation_guides.get(
            crop_name, f"Provide regular irrigation suitable for {crop_name}."
        )
        return [base]

    def _get_prevention_measures(self, disease_info, severity, weather_data):
        base = disease_info.get("prevention", [])
        extra = []
        if severity in ["Moderate", "Severe"]:
            extra = [
                "Quarantine affected area to prevent spread",
                "Increase frequency of crop monitoring",
                "Apply preventive treatment to neighboring healthy plants",
                "Disinfect farm tools after working in affected areas",
            ]
        if weather_data:
            if weather_data.get("humidity", 50) > 75:
                extra.append(
                    "High humidity period - increase preventive fungicide frequency"
                )
            if weather_data.get("rainfall", 0) > 5:
                extra.append("Rain expected - apply protective treatment before rain")
        return base + extra

    def _get_crop_management_tips(
        self, crop_name, disease_name, severity, weather_data
    ):
        tips = [
            f"Closely monitor {crop_name} plants daily for disease progression",
            "Remove and destroy severely infected plant parts",
            "Maintain proper plant spacing for air circulation",
            "Keep field free of weeds that may harbor pathogens",
        ]
        if severity in ["Moderate", "Severe"]:
            tips.extend(
                [
                    "Consider early harvesting if crop is mature enough",
                    f"Record disease progression in {crop_name} for future reference",
                    "Consult with local agricultural extension officer",
                    "Plan crop rotation to prevent disease recurrence next season",
                ]
            )
        return tips

    def _get_urgency(self, severity):
        urgency_map = {
            "Healthy": "No urgency",
            "Mild": "Low - treat within the week",
            "Moderate": "Medium - treat within 2-3 days",
            "Severe": "High - treat immediately",
        }
        return urgency_map.get(severity, "Unknown")
