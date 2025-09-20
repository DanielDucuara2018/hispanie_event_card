import requests
from datetime import datetime
from typing import Dict, Optional


class WeatherService:
    """Service to fetch weather data for motivation cards."""

    def __init__(self, api_key: str):
        """
        Initialize weather service with API key.

        Args:
            api_key: OpenWeatherMap API key
        """
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def get_weather_for_city(self, city: str, date: datetime) -> Optional[Dict]:
        """
        Get weather data for a specific city and date.

        Args:
            city: City name (e.g., "Paris", "Nantes")
            date: Date for weather forecast

        Returns:
            Weather data dictionary or None if error
        """
        try:
            # For current day, use current weather
            if date.date() == datetime.now().date():
                return self._get_current_weather(city)
            else:
                # For future dates, use forecast (up to 5 days)
                return self._get_forecast_weather(city, date)
        except Exception as e:
            print(f"Error fetching weather for {city}: {e}")
            return None

    def _get_current_weather(self, city: str) -> Optional[Dict]:
        """Get current weather for city."""
        url = f"{self.base_url}/weather"
        params = {"q": city, "appid": self.api_key, "units": "metric", "lang": "en"}

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return self._format_weather_data(data)
        return None

    def _get_forecast_weather(self, city: str, target_date: datetime) -> Optional[Dict]:
        """Get forecast weather for city and date."""
        url = f"{self.base_url}/forecast"
        params = {"q": city, "appid": self.api_key, "units": "metric", "lang": "en"}

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            # Find closest forecast to target date
            for forecast in data.get("list", []):
                forecast_date = datetime.fromtimestamp(forecast["dt"])
                if forecast_date.date() == target_date.date():
                    return self._format_weather_data(forecast)
        return None

    def _format_weather_data(self, data: Dict) -> Dict:
        """Format weather data for card display."""
        weather = data.get("weather", [{}])[0]
        main = data.get("main", {})

        return {
            "temperature": round(main.get("temp", 0)),
            "description": weather.get("description", "").title(),
            "icon": weather.get("icon", "01d"),
            "emoji": self._get_weather_emoji(weather.get("main", "")),
            "humidity": main.get("humidity", 0),
            "feels_like": round(main.get("feels_like", 0)),
        }

    def _get_weather_emoji(self, weather_main: str) -> str:
        """Get emoji for weather condition."""
        weather_emojis = {
            "Clear": "☀️",
            "Clouds": "☁️",
            "Rain": "🌧️",
            "Drizzle": "🌦️",
            "Thunderstorm": "⛈️",
            "Snow": "❄️",
            "Mist": "🌫️",
            "Fog": "🌫️",
            "Haze": "🌫️",
        }
        return weather_emojis.get(weather_main, "🌤️")
