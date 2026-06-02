from collections.abc import AsyncIterator

import httpx

from app.services.open_meteo import OpenMeteoClient
from app.services.weather_scores import WeatherScoresService


async def get_weather_scores_service() -> AsyncIterator[WeatherScoresService]:
    """Create the weather scores service for one API request."""
    # Keep the HTTP client request-scoped so sockets are opened and closed predictably.
    async with httpx.AsyncClient(timeout=15) as http_client:
        yield WeatherScoresService(weather_client=OpenMeteoClient(http_client=http_client))
