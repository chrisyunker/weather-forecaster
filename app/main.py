import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException
from datetime import datetime
from .db import Db
from .weather import Weather

LOGGING_LEVEL = logging.INFO
OFFICE = "LSX"
DB_NAME = "temperatures.db"
DEFAULT_REQ_FORECAST_PERIOD = "60"
QUERY_FORECAST_NUM_HOURS = 72

logging.basicConfig(level=LOGGING_LEVEL, format='%(levelname)s: %(message)s')

# Extract start-up configuration from environmental values
latitude = os.getenv("WEATHER_LATITUDE")
longitude = os.getenv("WEATHER_LONGITUDE")
if not latitude or not longitude:
    logging.error("Terminating application since latitude and/or longitude "
                  "values are not configured")
    sys.exit()
logging.info(f"Configured location: latitude: {latitude}, longitude: {longitude}")

forecast_period = int(os.getenv("WEATHER_REQ_FORECAST_PERIOD", DEFAULT_REQ_FORECAST_PERIOD))
logging.info(f"Configured forecast request period: {forecast_period} min")

# We need to translate lat/lon geographic coordinates to the grid coordinates 
# used by weather.gov before starting up
grid = Weather.get_grid(latitude, longitude)
if "error" in grid:
    logging.error(f"Terminating application since we failed to get the grid coordinates, "
                  f"error: {grid['error']}")
    sys.exit()

grid_x = int(grid["grid_x"])
grid_y = int(grid["grid_y"])
logging.info(f"Received grid coordinates: {grid_x}, {grid_y}, "
             f"for geographic coordinates: {latitude}, {longitude}")

# Create Database object wrapper
db = Db(DB_NAME)

# Function used to query forecasts and store results in the database
def get_and_store_forecasts():
    forecasts = Weather.get_forecasts(grid_x, grid_y, OFFICE, QUERY_FORECAST_NUM_HOURS)
    if "error" in forecasts:
        logging.warning(f"Failed to get forecasts for grid: {grid_x}, {grid_y}, "
                        f"office: {OFFICE}, error: {forecasts['error']}")
    else:
        for forecast in forecasts["forecasts"]:
            db.store_temp(forecast["epoch"], forecast["temperature"])
        logging.debug(f"Successfully Stored forecasts for grid: {grid_x}, {grid_y}")

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
    except ValueError as e:
        raise HTTPException(status_code=400,
                            detail=f"Invalid date: {date}, must be in format: YYYY-MM-DD")

    # First need to translate geographic coordinates into grid coordinates
    grid = Weather.get_grid(latitude, longitude)
    if "error" in grid:
        raise HTTPException(status_code=400,
                            detail=grid["error"])

    # If the grid coordinates do not match our grid coordinates,
    # then return 404 since we wont have that data
    if grid["grid_x"] != grid_x or grid["grid_y"] != grid_y:
        raise HTTPException(status_code=404,
                            detail="Location not found")

    # Query Db for low/high temps are return it if we have it
    temps = db.get_temps(epoch)
    if temps is None:
        raise HTTPException(status_code=404,
                            detail="Datetime not found")

    return {"low": temps["low"], "high": temps["high"]}

