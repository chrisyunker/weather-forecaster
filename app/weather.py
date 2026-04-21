"""
Weather class handles all API requests to api.weather.gov.
"""

import requests
from datetime import datetime

class Weather:
    def get_grid(latitude: str, longitude: str) -> dict:

        points_url = f"https://api.weather.gov/points/{latitude},{longitude}"
        points_headers = {"accept": "application/geo+json"}

        try:
            response = requests.get(points_url, headers=points_headers)
            response.raise_for_status()
            if response.status_code == 200:
                points_data = response.json()
                grid_x = int(points_data["properties"]["gridX"])
                grid_y = int(points_data["properties"]["gridY"])
                return {"grid_x": grid_x, "grid_y": grid_y}
            else:
                error_msg = f"Get grid request failed, code: {response.status_code}, response: {response.json()}"
                return {"error": error_msg}
        except requests.exceptions.RequestException as e:
            error_msg = f"Get grid request failed, error: {e}"
            return {"error": error_msg}


    def get_forecasts(grid_x: str, grid_y: str, office: str, num_hours: str) -> dict:

        forecast_url = f"https://api.weather.gov/gridpoints/{office}/{grid_x},{grid_y}/forecast/hourly"
        forecast_headers = {"accept": "application/geo+json"}

        try:
            response = requests.get(forecast_url, headers=forecast_headers)
            response.raise_for_status()
            if response.status_code == 200:
                forecast_data = response.json()
                periods = forecast_data["properties"]["periods"]
                forecasts = []
                for period in periods:
                    number = int(period["number"])
                    # Limit forecasts to the next number of hours based on 'num_hours'
                    if number <= num_hours:
                        start_time = period["startTime"]
                        end_time = period["endTime"]
                        temperature = period["temperature"]
                        epoch = int(datetime.fromisoformat(start_time).timestamp())
                        forecasts.append({"epoch": epoch, "temperature": temperature})
                return {"forecasts": forecasts}
            else:
                error_msg = f"Get forecast request failed, code: {response.status_code}, response: {response.json()}"
                return {"error": error_msg}
        except requests.exceptions.RequestException as e:
            error_msg = f"Get forcast request failed, error: {e}"
            return {"error": error_msg}

