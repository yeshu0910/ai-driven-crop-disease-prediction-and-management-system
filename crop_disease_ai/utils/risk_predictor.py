from datetime import datetime

import numpy as np


class RiskPredictor:
    def __init__(self, weather_api=None, knowledge_base=None):
        self.weather_api = weather_api
        self.knowledge_base = knowledge_base

        self.disease_risk_params = {
            "Tomato": {
                "optimal_temp": (22, 28),
                "high_humidity_threshold": 75,
                "wind_sensitivity": 0.6,
                "rain_sensitivity": 0.7,
            },
            "Potato": {
                "optimal_temp": (18, 24),
                "high_humidity_threshold": 80,
                "wind_sensitivity": 0.5,
                "rain_sensitivity": 0.8,
            },
            "Rice": {
                "optimal_temp": (24, 30),
                "high_humidity_threshold": 85,
                "wind_sensitivity": 0.4,
                "rain_sensitivity": 0.6,
            },
            "Wheat": {
                "optimal_temp": (15, 25),
                "high_humidity_threshold": 75,
                "wind_sensitivity": 0.7,
                "rain_sensitivity": 0.5,
            },
            "Corn": {
                "optimal_temp": (20, 28),
                "high_humidity_threshold": 75,
                "wind_sensitivity": 0.5,
                "rain_sensitivity": 0.6,
            },
            "Cotton": {
                "optimal_temp": (25, 32),
                "high_humidity_threshold": 70,
                "wind_sensitivity": 0.6,
                "rain_sensitivity": 0.4,
            },
            "Grapes": {
                "optimal_temp": (20, 27),
                "high_humidity_threshold": 75,
                "wind_sensitivity": 0.5,
                "rain_sensitivity": 0.7,
            },
            "Apple": {
                "optimal_temp": (15, 22),
                "high_humidity_threshold": 75,
                "wind_sensitivity": 0.5,
                "rain_sensitivity": 0.7,
            },
        }

    def predict_7_day_risk(self, crop_name, forecast_data, current_disease=None):
        if not forecast_data or "forecasts" not in forecast_data:
            return self._empty_risk_prediction(crop_name)

        forecasts = forecast_data.get("forecasts", [])[:7]
        risk_predictions = []

        for day_forecast in forecasts:
            risk = self._calculate_daily_risk(crop_name, day_forecast, current_disease)
            risk_predictions.append(risk)

        overall_risk = self._calculate_overall_risk(risk_predictions)

        return {
            "predictions": risk_predictions,
            "overall_risk": overall_risk,
            "crop_name": crop_name,
            "generated_at": datetime.now().isoformat(),
            "high_risk_days": sum(
                1 for r in risk_predictions if r["risk_level"] == "High"
            ),
            "medium_risk_days": sum(
                1 for r in risk_predictions if r["risk_level"] == "Medium"
            ),
            "preventive_actions": self._generate_preventive_actions(
                overall_risk, crop_name, risk_predictions
            ),
        }

    def _calculate_daily_risk(self, crop_name, forecast, current_disease):
        temp = forecast.get("temp_avg", 25)
        humidity = forecast.get("humidity_avg", 60)
        wind_speed = forecast.get("wind_speed_avg", 5)
        date = forecast.get("date", datetime.now().strftime("%Y-%m-%d"))
        description = forecast.get("description", "clear sky")

        risk_score = 0.0
        risk_factors = []

        crop_params = self.disease_risk_params.get(
            crop_name,
            {
                "optimal_temp": (20, 28),
                "high_humidity_threshold": 75,
                "wind_sensitivity": 0.5,
                "rain_sensitivity": 0.5,
            },
        )

        opt_temp_min, opt_temp_max = crop_params["optimal_temp"]
        if opt_temp_min <= temp <= opt_temp_max:
            risk_score += 25
            risk_factors.append(
                {
                    "factor": "temperature",
                    "detail": f"Temperature ({temp}°C) within optimal range for disease development",
                }
            )

        if humidity > crop_params["high_humidity_threshold"]:
            risk_score += 30
            risk_factors.append(
                {
                    "factor": "humidity",
                    "detail": f"Humidity ({humidity}%) exceeds safe threshold",
                }
            )
        elif humidity > 60:
            risk_score += 10
            risk_factors.append(
                {"factor": "humidity", "detail": f"Moderate humidity ({humidity}%)"}
            )

        if wind_speed > 8:
            risk_score += 15 * crop_params["wind_sensitivity"]
            risk_factors.append(
                {
                    "factor": "wind",
                    "detail": f"Wind speed ({wind_speed} m/s) aids spore dispersal",
                }
            )

        rain_indicators = ["rain", "drizzle", "thunderstorm", "shower"]
        if any(r in description.lower() for r in rain_indicators):
            risk_score += 20 * crop_params["rain_sensitivity"]
            risk_factors.append(
                {
                    "factor": "rain",
                    "detail": "Rain expected - creates favorable conditions for infection",
                }
            )

        if current_disease and "healthy" not in current_disease.lower():
            risk_score += 10

        risk_score = min(risk_score, 100)

        if risk_score < 30:
            risk_level = "Low"
        elif risk_score < 60:
            risk_level = "Medium"
        else:
            risk_level = "High"

        suggestions = self._get_day_suggestions(risk_level, risk_factors, crop_name)

        return {
            "date": date,
            "temp_avg": round(temp, 1),
            "humidity_avg": round(humidity, 1),
            "wind_speed_avg": round(wind_speed, 1),
            "weather_description": description,
            "risk_score": round(risk_score, 1),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "suggestions": suggestions,
        }

    def _get_day_suggestions(self, risk_level, risk_factors, crop_name):
        suggestions = []
        if risk_level == "High":
            suggestions.append(f"Apply protective fungicide to {crop_name}")
            suggestions.append("Monitor crop twice daily")
            suggestions.append("Ensure drainage systems are clear")
        elif risk_level == "Medium":
            suggestions.append(f"Inspect {crop_name} for early symptoms")
            suggestions.append("Consider preventive treatment")
        else:
            suggestions.append(f"Continue routine {crop_name} monitoring")

        for rf in risk_factors:
            if rf["factor"] == "rain":
                suggestions.append("Delay irrigation if rain expected")
            elif rf["factor"] == "wind":
                suggestions.append("Check for wind damage and entry points")
            elif rf["factor"] == "humidity":
                suggestions.append("Improve air circulation in crop canopy")

        return suggestions

    def _calculate_overall_risk(self, risk_predictions):
        if not risk_predictions:
            return {"risk_level": "Low", "risk_score": 0}

        avg_score = np.mean([r["risk_score"] for r in risk_predictions])
        max_score = max(r["risk_score"] for r in risk_predictions)

        combined = 0.6 * avg_score + 0.4 * max_score

        if combined < 30:
            level = "Low"
        elif combined < 60:
            level = "Medium"
        else:
            level = "High"

        return {
            "risk_level": level,
            "risk_score": round(combined, 1),
            "avg_risk_score": round(avg_score, 1),
            "max_risk_score": round(max_score, 1),
        }

    def _generate_preventive_actions(self, overall_risk, crop_name, predictions):
        actions = []
        risk_level = overall_risk["risk_level"]

        if risk_level == "High":
            actions.extend(
                [
                    f"URGENT: Apply protective treatment to {crop_name} immediately",
                    "Schedule daily crop monitoring",
                    "Prepare fungicide application equipment",
                    "Ensure adequate drainage around plants",
                    "Consider early harvest if crop is mature",
                ]
            )
        elif risk_level == "Medium":
            actions.extend(
                [
                    f"Schedule preventive fungicide application for {crop_name}",
                    "Increase monitoring frequency to every other day",
                    "Check weather forecast daily for updates",
                    "Review disease management plan",
                ]
            )
        else:
            actions.extend(
                [
                    f"Continue standard monitoring for {crop_name}",
                    "Maintain good crop management practices",
                    "Review and update disease management records",
                ]
            )

        high_risk_days = [p["date"] for p in predictions if p["risk_level"] == "High"]
        if high_risk_days:
            days_str = ", ".join(high_risk_days[:3])
            actions.append(f"Plan preventive measures for high-risk days: {days_str}")

        return actions

    def _empty_risk_prediction(self, crop_name):
        return {
            "predictions": [],
            "overall_risk": {"risk_level": "Unknown", "risk_score": 0},
            "crop_name": crop_name,
            "generated_at": datetime.now().isoformat(),
            "high_risk_days": 0,
            "medium_risk_days": 0,
            "preventive_actions": ["Enable weather API to get risk predictions"],
        }
