#!/usr/bin/env bash

# Script for testing locally, outside docker container

export WEATHER_LATITUDE=38.633068
export WEATHER_LONGITUDE=-90.305619
export WEATHER_REQ_FORECAST_PERIOD=1

./.venv/bin/fastapi run ./app/main.py


