from app.core.cities import CITIES
from app.services.open_meteo import HourlyWeatherData
from app.services.weather_scores.aggregation import average, score_city


def test_average_returns_rounded_arithmetic_mean() -> None:
    assert average([1, 2, 2]) == 1.67


def test_score_city_aggregates_hourly_weather_before_scoring() -> None:
    city_score = score_city(
        city=CITIES[0],
        hourly_weather=HourlyWeatherData(
            time=["2026-06-01T00:00", "2026-06-01T01:00"],
            temperature_2m=[23, 25],
            wind_speed_10m=[0, 2],
            relative_humidity_2m=[45, 55],
            cloud_cover=[20, 30],
        ),
    )

    assert city_score.rank == 0
    assert city_score.averages.temperature_2m == 24
    assert city_score.averages.wind_speed_10m == 1
    assert city_score.scores.total == 9.8
