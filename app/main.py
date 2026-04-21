import os
import logging
import sys
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException
from .db import Db
from .weather import Weather

LOGGING_LEVEL = logging.INFO
OFFICE = "LSX"
DB_NAME = "temperatures.db"
DEFAULT_REQ_FORECAST_PERIOD = "60"
QUERY_FORECAST_NUM_HOURS = 72

logging.basicConfig(
    level=LOGGING_LEVEL,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

# Extract start-up configuration from environmental values
app_latitude = os.getenv("WEATHER_LATITUDE")
app_longitude = os.getenv("WEATHER_LONGITUDE")
if not app_latitude or not app_longitude:
    logging.error("Terminating application since latitude and/or longitude "
                  "values are not configured")
    sys.exit()
logging.info(f"Configured location: latitude: {app_latitude}, longitude: {app_longitude}")

forecast_period = int(os.getenv("WEATHER_REQ_FORECAST_PERIOD", DEFAULT_REQ_FORECAST_PERIOD))
logging.info(f"Configured forecast request period: {forecast_period} min")

# We need to translate lat/lon geographic coordinates to the grid coordinates
# used by weather.gov before starting up
app_grid = Weather.get_grid(app_latitude, app_longitude)
if "error" in app_grid:
    logging.error(f"Terminating application since we failed to get the grid coordinates, "
                  f"error: {app_grid['error']}")
    sys.exit()

app_grid_x = int(app_grid["grid_x"])
app_grid_y = int(app_grid["grid_y"])
logging.info(f"Received grid coordinates: {app_grid_x}, {app_grid_y}, "
             f"for geographic coordinates: {app_latitude}, {app_longitude}")

# Create Database object wrapper
db = Db(DB_NAME)

# Function used to query forecasts and store results in the database
def get_and_store_forecasts():
    forecasts = Weather.get_forecasts(app_grid_x, app_grid_y, OFFICE, QUERY_FORECAST_NUM_HOURS)
    if "error" in forecasts:
        logging.warning(f"Failed to get forecasts for grid: {app_grid_x}, {app_grid_y}, "
                        f"office: {OFFICE}, error: {forecasts['error']}")
    else:
        for forecast in forecasts["forecasts"]:
            db.store_temp(forecast["epoch"], forecast["temperature"])
        logging.debug(f"Successfully Stored forecasts for grid: {app_grid_x}, {app_grid_y}")

# Run an initial query to populate database
get_and_store_forecasts()

# Set up scheduler to periodicly query forecasts based on configured request period
scheduler = BackgroundScheduler()
scheduler.add_job(get_and_store_forecasts, 'interval', minutes=forecast_period)
scheduler.start()

# Start hosting REST interface
app = FastAPI()

@app.get("/v1/forecast")
def get_temps(lat: str, lon: str, date: str, hour: int):

    # Hour value must be between 0-23
    if hour < 0 or hour > 23:
        raise HTTPException(status_code=400,
                            detail=f"Invalid hour: {hour}, must be between 0-23")

    # Create epoch timestamp from date and hour fields
    try:
        dt = f"{date}T{hour:02d}:00:00+00:00"
        epoch = int(datetime.fromisoformat(dt).timestamp())
    except ValueError as _e:
        raise HTTPException(status_code=400,
                            detail=f"Invalid date: {date}, must be in format: YYYY-MM-DD")

    # First need to translate geographic coordinates into grid coordinates
    grid = Weather.get_grid(lat, lon)
    if "error" in grid:
        raise HTTPException(status_code=400,
                            detail=grid["error"])

    # If the grid coordinates do not match our grid coordinates,
    # then return 404 since we wont have that data
    if grid["grid_x"] != app_grid_x or grid["grid_y"] != app_grid_y:
        raise HTTPException(status_code=404,
                            detail="Location not found")

    # Query Db for low/high temps are return it if we have it
    temps = db.get_temps(epoch)
    if temps is None:
        raise HTTPException(status_code=404,
                            detail="Datetime not found")

    return {"low": temps["low"], "high": temps["high"]}
