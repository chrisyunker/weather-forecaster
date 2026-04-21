# Weather Forecaster

The application queries, processes, and hosts weather forecasting data based on the requirements listed in the assigned coding challange.


## Build and Run

This application uses a docker compose file to build and run.

First, clone this repo and change directories into the repo:
```
git clone https://github.com/chrisyunker/weather-forecaster.git
cd weather-forecaster
```

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

For configuration, there is an included `weather-forecaster.env` file with default settings. To change, update the values in the file and restart the docker container.

| Parameter | Value |
|-----------|-------|
| WEATHER_LATITUDE | Latitude of forecasted location |
| WEATHER_LONGITUDE | Longitude of forecasted location |
| WEATHER_REQ_FORECAST_PERIOD | Request period in minutes |


## API

Get the low and high temperatures for a geographic location for a specific UTC datetime (restricted to hourly values)

`GET /v1/forecast`

This request requires the following query parameters:

| Parameter | Value |
|-----------|-------|
| lat | Geographical latitude |
| lon | Geographical longitude |
| date | Forecast UTC date in the format (YYYY-MM-DD) |
| hour | Forecast UTC hour (0 - 23) |

A successful query will return a JSON body with the following parameters:

| Parameter | Value |
|-----------|-------|
| low | Lowest forecasted temperature (F) |
| high | Highest forecasted temperature (F) |


Example Request
```
curl "http://127.0.0.1:8088/v1/forecast?lat=38.654596&lon=-90.301272&date=2026-04-20&hour=23"
```
Example Response
```
{'low': 60, 'high': 79}
```

