import asyncio

from app.core.cities import CITIES, City
from app.core.date_range import DateRange
from app.services.open_meteo import OpenMeteoClient
from app.services.weather_scores.aggregation import score_city
from app.services.weather_scores.ranking import rank_city_scores
from app.services.weather_scores.schemas import CitiesScores
from app.services.weather_scores.validation import validate_historical_range


class WeatherScoresService:
    """Use case service for building ranked city weather scores."""

    def __init__(
        self,
        weather_client: OpenMeteoClient,
        cities: tuple[City, ...] = CITIES,
    ) -> None:
        """Create the service with an Open-Meteo client and configured cities."""
        self._weather_client = weather_client
        self._cities = cities

    async def get_cities_scores(self, date_range: DateRange) -> CitiesScores:
        """Fetch weather data and return ranked city scores for a date range."""
        validate_historical_range(date_range=date_range)

        # Each city fetch is independent, so concurrent calls keep the endpoint responsive.
        hourly_results = await asyncio.gather(
            *(
                self._weather_client.fetch_hourly_weather(city=city, date_range=date_range)
                for city in self._cities
            )
        )

        city_scores = [
            score_city(city=city, hourly_weather=hourly_weather)
            for city, hourly_weather in zip(self._cities, hourly_results, strict=True)
        ]

        return CitiesScores(
            start_date=date_range.start_date,
            end_date=date_range.end_date,
            cities=rank_city_scores(city_scores),
        )
