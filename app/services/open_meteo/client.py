from typing import Any

import httpx

from app.core.cities import City
from app.core.date_range import DateRange
from app.services.open_meteo.exceptions import OpenMeteoError
from app.services.open_meteo.payload import build_weather_params, parse_hourly_weather
from app.services.open_meteo.schemas import HourlyWeatherData

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


class OpenMeteoClient:
    """Async client for fetching hourly historical weather data from Open-Meteo."""

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        base_url: str = OPEN_METEO_ARCHIVE_URL,
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

        return parse_hourly_weather(payload=_read_json(response=response, city=city), city=city)


def _read_json(response: httpx.Response, city: City) -> dict[str, Any]:
    """Read an Open-Meteo response as JSON object."""
    try:
        payload = response.json()
    except ValueError as exc:
        msg = f"Open-Meteo returned invalid JSON for {city.name}."
        raise OpenMeteoError(msg) from exc

    if not isinstance(payload, dict):
        msg = f"Open-Meteo returned invalid JSON object for {city.name}."
        raise OpenMeteoError(msg)

    return payload
