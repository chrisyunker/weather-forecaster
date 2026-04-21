"""
Script used for testing the Weather class
"""
import logging
import os
from app.weather import Weather

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Good test
grid = Weather.get_grid(38.654, -90.301)
print(f"Grid: {grid}")

# Bad GPS value test
grid = Weather.get_grid(138.654, -190.301)
print(f"Grid: {grid}")
print()

# Good test
forecasts = Weather.get_forecasts(92, 75, "LSX")
print(f"Forcasts: {forecasts}")
print()

# Bad grid value test
forecasts = Weather.get_forecasts(192, -75, "LSX")
print(f"Forcasts: {forecasts}")
print()

# Bad office value test
forecasts = Weather.get_forecasts(92, 75, "XXX")
print(f"Forcasts: {forecasts}")
print()


