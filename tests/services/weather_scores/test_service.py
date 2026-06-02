import asyncio
from datetime import date, timedelta

import pytest

from app.core.cities import CITIES, City
from app.core.date_range import DateRange
from app.services.open_meteo import HourlyWeatherData, OpenMeteoError
from app.services.weather_scores import WeatherScoresService


def test_weather_scores_service_aggregates_scores_and_sorts_cities() -> None:
    weather_by_city = {
        "Warsaw": _hourly_weather(
            temperature=[24, 24],
            wind=[0, 0],
            humidity=[50, 50],
            cloud=[25, 25],
        ),
        "Gdansk": _hourly_weather(
            temperature=[30, 30],
            wind=[8, 8],
            humidity=[90, 90],
            cloud=[90, 90],
        ),
    }
    service = WeatherScoresService(
        weather_client=FakeWeatherClient(weather_by_city),
        cities=CITIES[:2],
    )

    result = asyncio.run(service.get_cities_scores(_yesterday_range()))

    assert [city_score.city.name for city_score in result.cities] == ["Warsaw", "Gdansk"]
    assert [city_score.rank for city_score in result.cities] == [1, 2]
    assert result.cities[0].averages.temperature_2m == 24
    assert result.cities[0].scores.total == 10


def test_weather_scores_service_preserves_config_order_when_scores_are_equal() -> None:
    weather_by_city = {
        "Warsaw": _hourly_weather(temperature=[24], wind=[0], humidity=[50], cloud=[25]),
        "Gdansk": _hourly_weather(temperature=[24], wind=[0], humidity=[50], cloud=[25]),
    }
    service = WeatherScoresService(
        weather_client=FakeWeatherClient(weather_by_city),
        cities=CITIES[:2],
    )

    result = asyncio.run(service.get_cities_scores(_yesterday_range()))

    assert [city_score.city.name for city_score in result.cities] == ["Warsaw", "Gdansk"]


def test_weather_scores_service_rejects_future_date_ranges() -> None:
    service = WeatherScoresService(weather_client=FakeWeatherClient({}), cities=())
    future_range = DateRange(start_date=date.today(), end_date=date.today())

    with pytest.raises(ValueError, match="yesterday"):
        asyncio.run(service.get_cities_scores(future_range))


def test_weather_scores_service_propagates_open_meteo_errors() -> None:
    service = WeatherScoresService(
        weather_client=FailingWeatherClient(),
        cities=CITIES[:1],
    )

    with pytest.raises(OpenMeteoError):
        asyncio.run(service.get_cities_scores(_yesterday_range()))


class FakeWeatherClient:
    def __init__(self, weather_by_city: dict[str, HourlyWeatherData]) -> None:
        self._weather_by_city = weather_by_city

    async def fetch_hourly_weather(
        self,
        city: City,
        date_range: DateRange,
    ) -> HourlyWeatherData:
        return self._weather_by_city[city.name]


class FailingWeatherClient:
    async def fetch_hourly_weather(
        self,
        city: City,
        date_range: DateRange,
    ) -> HourlyWeatherData:
        raise OpenMeteoError("Open-Meteo request failed.")


def _hourly_weather(
    *,
    temperature: list[float],
    wind: list[float],
    humidity: list[float],
    cloud: list[float],
) -> HourlyWeatherData:
    return HourlyWeatherData(
        time=["2026-06-01T00:00"],
        temperature_2m=temperature,
        wind_speed_10m=wind,
        relative_humidity_2m=humidity,
        cloud_cover=cloud,
    )


def _yesterday_range() -> DateRange:
    yesterday = date.today() - timedelta(days=1)
    return DateRange(start_date=yesterday, end_date=yesterday)
