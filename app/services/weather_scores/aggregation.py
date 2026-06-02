from app.core.cities import City
from app.services.open_meteo import HourlyWeatherData
from app.services.scoring import calculate_weather_scores
from app.services.weather_scores.schemas import CityWeatherScore, WeatherAverages


def score_city(city: City, hourly_weather: HourlyWeatherData) -> CityWeatherScore:
    """Build a score object for one city from raw hourly weather values."""
    averages = WeatherAverages(
        temperature_2m=average(hourly_weather.temperature_2m),
        wind_speed_10m=average(hourly_weather.wind_speed_10m),
        relative_humidity_2m=average(hourly_weather.relative_humidity_2m),
        cloud_cover=average(hourly_weather.cloud_cover),
    )
    scores = calculate_weather_scores(
        temperature_2m=averages.temperature_2m,
        wind_speed_10m=averages.wind_speed_10m,
        relative_humidity_2m=averages.relative_humidity_2m,
        cloud_cover=averages.cloud_cover,
    )

    # Ranking is assigned after all city scores are sorted.
    return CityWeatherScore(rank=0, city=city, averages=averages, scores=scores)


def average(values: list[float]) -> float:
    """Calculate the rounded arithmetic mean used in weather score input."""
    return round(sum(values) / len(values), 2)
