import requests
import random
from datetime import datetime

class WeatherAPI:
    def __init__(self, use_mock=True, api_key=None):
        self.use_mock = use_mock
        self.api_key = api_key

    def get_current_weather(self, city):
        """Get current weather data - uses mock data for POC"""
        if self.use_mock or not self.api_key:
            return self._get_mock_weather_data(city)
        else:
            return self._get_real_weather_data(city)

    def _get_mock_weather_data(self, city):
        """Generate realistic mock weather data based on city and season"""
        # Seasonal adjustments
        now = datetime.now()
        month = now.month

        # Base temperature ranges by season (for northern hemisphere)
        if month in [12, 1, 2]:  # Winter
            base_temp_range = (-10, 10)
        elif month in [3, 4, 5]:  # Spring
            base_temp_range = (5, 25)
        elif month in [6, 7, 8]:  # Summer
            base_temp_range = (15, 35)
        else:  # Fall
            base_temp_range = (5, 20)

        # City-specific adjustments
        city_adjustments = {
            "New York": {"temp_adjust": 0, "humidity_adjust": 5},
            "London": {"temp_adjust": -5, "humidity_adjust": 10},
            "Tokyo": {"temp_adjust": 3, "humidity_adjust": 15},
            "Sydney": {"temp_adjust": 8, "humidity_adjust": -5},
            "Paris": {"temp_adjust": -2, "humidity_adjust": 0},
            "Berlin": {"temp_adjust": -3, "humidity_adjust": -2},
            "Mumbai": {"temp_adjust": 15, "humidity_adjust": 25}
        }

        adjustment = city_adjustments.get(city, {"temp_adjust": 0, "humidity_adjust": 0})

        weather_patterns = {
            "Clear": {
                "temp_range": (base_temp_range[0] + 5 + adjustment["temp_adjust"],
                              base_temp_range[1] + adjustment["temp_adjust"]),
                "humidity_range": (30 + adjustment["humidity_adjust"],
                                  60 + adjustment["humidity_adjust"]),
                "pressure_range": (1010, 1030),
                "wind_range": (0, 10)
            },
            "Cloudy": {
                "temp_range": (base_temp_range[0] + adjustment["temp_adjust"],
                              base_temp_range[1] - 5 + adjustment["temp_adjust"]),
                "humidity_range": (50 + adjustment["humidity_adjust"],
                                  80 + adjustment["humidity_adjust"]),
                "pressure_range": (1000, 1020),
                "wind_range": (5, 15)
            },
            "Rain": {
                "temp_range": (base_temp_range[0] - 2 + adjustment["temp_adjust"],
                              base_temp_range[1] - 8 + adjustment["temp_adjust"]),
                "humidity_range": (70 + adjustment["humidity_adjust"],
                                  95 + adjustment["humidity_adjust"]),
                "pressure_range": (980, 1010),
                "wind_range": (10, 25)
            },
            "Snow": {
                "temp_range": (-10 + adjustment["temp_adjust"],
                              5 + adjustment["temp_adjust"]),
                "humidity_range": (60 + adjustment["humidity_adjust"],
                                  85 + adjustment["humidity_adjust"]),
                "pressure_range": (990, 1020),
                "wind_range": (5, 20)
            },
            "Fog": {
                "temp_range": (base_temp_range[0] + adjustment["temp_adjust"],
                              base_temp_range[1] - 3 + adjustment["temp_adjust"]),
                "humidity_range": (80 + adjustment["humidity_adjust"],
                                  98 + adjustment["humidity_adjust"]),
                "pressure_range": (1005, 1025),
                "wind_range": (0, 5)
            },
            "Thunderstorm": {
                "temp_range": (base_temp_range[0] + adjustment["temp_adjust"],
                              base_temp_range[1] - 5 + adjustment["temp_adjust"]),
                "humidity_range": (75 + adjustment["humidity_adjust"],
                                  98 + adjustment["humidity_adjust"]),
                "pressure_range": (970, 1005),
                "wind_range": (15, 35)
            }
        }

        # Weighted random selection for more realistic weather distribution
        weather_weights = {
            "Clear": 0.3,
            "Cloudy": 0.4,
            "Rain": 0.15,
            "Snow": 0.05,
            "Fog": 0.05,
            "Thunderstorm": 0.05
        }

        description = random.choices(
            list(weather_weights.keys()),
            weights=list(weather_weights.values())
        )[0]

        pattern = weather_patterns[description]

        temperature = random.uniform(*pattern["temp_range"])
        humidity = random.randint(*pattern["humidity_range"])
        pressure = random.randint(*pattern["pressure_range"])
        wind_speed = random.uniform(*pattern["wind_range"])

        return {
            "city": city,
            "temperature": round(temperature, 1),
            "humidity": humidity,
            "pressure": pressure,
            "wind_speed": round(wind_speed, 1),
            "description": description,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _get_real_weather_data(self, city):
        """Get real weather data from OpenWeatherMap API"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                return {
                    "city": city,
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "wind_speed": data["wind"]["speed"],
                    "description": data["weather"][0]["main"],
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                # Fallback to mock data if API fails
                return self._get_mock_weather_data(city)

        except Exception as e:
            print(f"Error fetching real weather data: {e}")
            # Fallback to mock data
            return self._get_mock_weather_data(city)

    def get_weather_forecast(self, city, days=5):
        """Get weather forecast (mock implementation)"""
        forecast = []
        for i in range(days):
            daily_weather = self._get_mock_weather_data(city)
            # Adjust temperature slightly for forecast days
            daily_weather['temperature'] += random.uniform(-2, 2)
            daily_weather['day'] = i + 1
            forecast.append(daily_weather)

        return forecast