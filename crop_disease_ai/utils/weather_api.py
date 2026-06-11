import requests
import json
import logging
from datetime import datetime, timedelta
from utils.config import OPENWEATHER_API_KEY, WEATHER_API_BASE_URL

logger = logging.getLogger(__name__)


class WeatherAPI:
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY

    def is_configured(self):
        return bool(self.api_key)

    def get_current_weather(self, location):
        if not self.is_configured():
            return self._mock_weather(location)
        try:
            if self._is_city_name(location):
                url = f"{WEATHER_API_BASE_URL}/weather"
                params = {"q": location, "appid": self.api_key, "units": "metric"}
            else:
                url = f"{WEATHER_API_BASE_URL}/weather"
                lat, lon = map(float, location.split(","))
                params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._parse_current_weather(data)
            else:
                logger.warning(f"Weather API error: {response.status_code}")
                return self._mock_weather(location)
        except Exception as e:
            logger.error(f"Weather request failed: {e}")
            return self._mock_weather(location)

    def get_forecast(self, location, days=7):
        if not self.is_configured():
            return self._mock_forecast(location, days)
        try:
            if self._is_city_name(location):
                url = f"{WEATHER_API_BASE_URL}/forecast"
                params = {"q": location, "appid": self.api_key, "units": "metric", "cnt": days * 8}
            else:
                url = f"{WEATHER_API_BASE_URL}/forecast"
                lat, lon = map(float, location.split(","))
                params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric", "cnt": days * 8}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._parse_forecast(data, days)
            else:
                logger.warning(f"Forecast API error: {response.status_code}")
                return self._mock_forecast(location, days)
        except Exception as e:
            logger.error(f"Forecast request failed: {e}")
            return self._mock_forecast(location, days)

    def _is_city_name(self, location):
        return not any(c.isdigit() for c in location) or "," not in location

    def _parse_current_weather(self, data):
        return {
            "location": data.get("name", "Unknown"),
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "weather_description": data["weather"][0]["description"],
            "weather_icon": data["weather"][0]["icon"],
            "clouds": data["clouds"]["all"],
            "lat": data["coord"]["lat"],
            "lon": data["coord"]["lon"],
            "timestamp": datetime.now().isoformat(),
            "source": "api"
        }

    def _parse_forecast(self, data, days):
        forecasts = []
        daily_data = {}
        for item in data["list"]:
            dt = datetime.fromtimestamp(item["dt"])
            date_key = dt.strftime("%Y-%m-%d")
            if date_key not in daily_data:
                daily_data[date_key] = {
                    "date": date_key,
                    "temps": [],
                    "humidities": [],
                    "wind_speeds": [],
                    "pressures": [],
                    "descriptions": [],
                    "weather_icons": []
                }
            daily_data[date_key]["temps"].append(item["main"]["temp"])
            daily_data[date_key]["humidities"].append(item["main"]["humidity"])
            daily_data[date_key]["wind_speeds"].append(item["wind"]["speed"])
            daily_data[date_key]["pressures"].append(item["main"]["pressure"])
            daily_data[date_key]["descriptions"].append(item["weather"][0]["description"])
            daily_data[date_key]["weather_icons"].append(item["weather"][0]["icon"])

        for date_key in sorted(list(daily_data.keys()))[:days]:
            dd = daily_data[date_key]
            forecasts.append({
                "date": date_key,
                "temp_min": min(dd["temps"]),
                "temp_max": max(dd["temps"]),
                "temp_avg": sum(dd["temps"]) / len(dd["temps"]),
                "humidity_avg": sum(dd["humidities"]) / len(dd["humidities"]),
                "wind_speed_avg": sum(dd["wind_speeds"]) / len(dd["wind_speeds"]),
                "pressure_avg": sum(dd["pressures"]) / len(dd["pressures"]),
                "description": max(set(dd["descriptions"]), key=dd["descriptions"].count),
                "weather_icon": dd["weather_icons"][len(dd["weather_icons"]) // 2]
            })
        return {"forecasts": forecasts, "location": data["city"]["name"], "source": "api"}

    def _mock_weather(self, location):
        import random
        random.seed(hash(location) % (2 ** 32))
        return {
            "location": location if self._is_city_name(location) else "Farm Location",
            "temperature": round(28 + random.random() * 12, 1),
            "feels_like": round(26 + random.random() * 10, 1),
            "humidity": round(50 + random.random() * 40, 1),
            "pressure": round(1000 + random.random() * 30, 1),
            "wind_speed": round(2 + random.random() * 8, 1),
            "weather_description": random.choice([
                "clear sky", "few clouds", "scattered clouds",
                "broken clouds", "light rain", "moderate rain",
                "overcast clouds"
            ]),
            "weather_icon": "01d",
            "clouds": round(random.random() * 100, 1),
            "lat": 0,
            "lon": 0,
            "timestamp": datetime.now().isoformat(),
            "source": "mock"
        }

    def _mock_forecast(self, location, days):
        import random
        random.seed(hash(location) % (2 ** 32))
        forecasts = []
        base_temp = 28 + random.random() * 8
        for i in range(days):
            date = (datetime.now() + timedelta(days=i + 1)).strftime("%Y-%m-%d")
            temp_var = random.uniform(-3, 3)
            forecasts.append({
                "date": date,
                "temp_min": round(base_temp + temp_var - 2, 1),
                "temp_max": round(base_temp + temp_var + 4, 1),
                "temp_avg": round(base_temp + temp_var + 1, 1),
                "humidity_avg": round(55 + random.random() * 35, 1),
                "wind_speed_avg": round(2 + random.random() * 6, 1),
                "pressure_avg": round(1005 + random.random() * 20, 1),
                "description": random.choice([
                    "clear sky", "few clouds", "scattered clouds",
                    "broken clouds", "light rain"
                ]),
                "weather_icon": "01d"
            })
        return {"forecasts": forecasts, "location": location if self._is_city_name(location) else "Farm Location", "source": "mock"}

    def get_disease_risk_from_weather(self, weather_data, crop_name):
        risk_score = 0
        risk_factors = []

        humidity = weather_data.get("humidity", 50)
        temperature = weather_data.get("temperature", 25)
        wind_speed = weather_data.get("wind_speed", 5)
        rainfall = weather_data.get("rainfall", 0)

        if humidity > 80:
            risk_score += 30
            risk_factors.append("High humidity (>80%) promotes fungal growth")
        elif humidity > 65:
            risk_score += 15
            risk_factors.append("Moderate humidity supports disease development")

        if 20 <= temperature <= 30:
            risk_score += 20
            risk_factors.append(f"Optimal temperature ({temperature}°C) for many pathogens")
        elif temperature > 35:
            risk_score += 10
            risk_factors.append("High temperature stress weakens plant defenses")

        if wind_speed > 10:
            risk_score += 15
            risk_factors.append("Strong wind aids spore dispersal")
        elif wind_speed > 5:
            risk_score += 5
            risk_factors.append("Moderate wind may spread pathogens")

        if rainfall > 5:
            risk_score += 20
            risk_factors.append("Rainfall creates favorable conditions for infection")
        elif rainfall > 2:
            risk_score += 10
            risk_factors.append("Light rainfall increases humidity around plants")

        risk_score = min(risk_score, 100)

        if risk_score < 30:
            risk_level = "Low"
        elif risk_score < 60:
            risk_level = "Medium"
        else:
            risk_level = "High"

        suggestions = self._get_risk_suggestions(risk_level, risk_factors, crop_name)

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "suggestions": suggestions,
            "crop_name": crop_name
        }

    def _get_risk_suggestions(self, risk_level, risk_factors, crop_name):
        suggestions = []
        if risk_level == "High":
            suggestions.extend([
                f"Apply fungicide to {crop_name} immediately",
                f"Increase monitoring frequency for {crop_name}",
                "Ensure proper drainage around plants",
                "Consider applying protective copper-based sprays",
                "Remove and destroy any infected plant material"
            ])
        elif risk_level == "Medium":
            suggestions.extend([
                f"Monitor {crop_name} plants daily for early symptoms",
                "Apply preventive fungicide if favorable conditions persist",
                "Improve air circulation through proper spacing",
                "Avoid overhead irrigation during high humidity periods"
            ])
        else:
            suggestions.extend([
                f"Continue routine monitoring of {crop_name} crop",
                "Maintain proper crop nutrition for disease resistance",
                "Follow regular preventive spraying schedule"
            ])

        for factor in risk_factors:
            if "humidity" in factor.lower():
                suggestions.append("Improve ventilation and reduce plant density")
            elif "temperature" in factor.lower():
                suggestions.append("Use shade nets if temperatures are extreme")
            elif "wind" in factor.lower():
                suggestions.append("Install windbreaks to reduce spore dispersal")
            elif "rain" in factor.lower() or "rainfall" in factor.lower():
                suggestions.append("Ensure proper field drainage after rainfall")

        return suggestions
