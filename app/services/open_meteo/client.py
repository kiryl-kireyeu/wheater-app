from typing import Any

import httpx

from app.core.cities import City
from app.core.date_range import DateRange
from app.services.open_meteo.exceptions import OpenMeteoError
from app.services.open_meteo.payload import (
    build_weather_params,
    build_weather_params_for_cities,
    parse_hourly_weather,
    parse_hourly_weather_list,
)
from app.services.open_meteo.schemas import HourlyWeatherData

OPEN_METEO_HISTORICAL_FORECAST_URL = "https://historical-forecast-api.open-meteo.com/v1/forecast"


class OpenMeteoClient:
    """Async client for fetching hourly historical weather data from Open-Meteo."""

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        base_url: str = OPEN_METEO_HISTORICAL_FORECAST_URL,
    ) -> None:
        self._http_client = http_client
        self._base_url = base_url

    async def fetch_hourly_weather(
        self,
        city: City,
        date_range: DateRange,
    ) -> HourlyWeatherData:
        """Fetch and validate hourly weather data for a city and date range."""
        try:
            response = await self._http_client.get(
                self._base_url,
                params=build_weather_params(city=city, date_range=date_range),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            msg = f"Open-Meteo returned HTTP {exc.response.status_code} for {city.name}."
            raise OpenMeteoError(msg) from exc
        except httpx.RequestError as exc:
            msg = f"Open-Meteo request failed for {city.name}."
            raise OpenMeteoError(msg) from exc

        return parse_hourly_weather(
            payload=_read_json_object(response=response, city=city),
            city=city,
        )

    async def fetch_hourly_weather_for_cities(
        self,
        cities: tuple[City, ...],
        date_range: DateRange,
    ) -> list[HourlyWeatherData]:
        """Fetch and validate hourly weather data for multiple cities in one request."""
        if not cities:
            return []

        try:
            response = await self._http_client.get(
                self._base_url,
                params=build_weather_params_for_cities(cities=cities, date_range=date_range),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            msg = f"Open-Meteo returned HTTP {exc.response.status_code} for city batch."
            raise OpenMeteoError(msg) from exc
        except httpx.RequestError as exc:
            msg = "Open-Meteo batch request failed."
            raise OpenMeteoError(msg) from exc

        return parse_hourly_weather_list(
            payload=_read_json(response=response, context="city batch"),
            cities=cities,
        )


def _read_json(response: httpx.Response, context: str) -> Any:
    """Read an Open-Meteo response as raw JSON payload."""
    try:
        return response.json()
    except ValueError as exc:
        msg = f"Open-Meteo returned invalid JSON for {context}."
        raise OpenMeteoError(msg) from exc


def _read_json_object(response: httpx.Response, city: City) -> dict[str, Any]:
    """Read an Open-Meteo single-city response as JSON object."""
    payload = _read_json(response=response, context=city.name)

    if not isinstance(payload, dict):
        msg = f"Open-Meteo returned invalid JSON object for {city.name}."
        raise OpenMeteoError(msg)

    return payload
