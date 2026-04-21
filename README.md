# Weather Forecaster

## Build and Run

Build image:

```
docker compose build
```

Run image:

```
docker compose up
```

Stop image:

```
docker compose down
```

## Configuration

Configurations are set via the `weather-forecaster.env` file.

| Parameter | Value |
|-----------|-------|
| WEATHER_LATITUDE | Latitude of forecasted location |
| WEATHER_LONGITUDE | Longitude of forecasted location |
| WEATHER_REQ_FORECAST_PERIOD | Request period in minutes |

