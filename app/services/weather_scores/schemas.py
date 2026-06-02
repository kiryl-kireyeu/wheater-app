from dataclasses import dataclass
from datetime import date

from app.core.cities import City
from app.services.scoring import WeatherScores


@dataclass(frozen=True, slots=True)
class WeatherAverages:
    """Stores averaged weather metrics used as scoring input."""

    temperature_2m: float
    wind_speed_10m: float
    relative_humidity_2m: float
    cloud_cover: float


@dataclass(frozen=True, slots=True)
class CityWeatherScore:
    """Represents one city's weather averages, component scores, and rank."""

    rank: int
    city: City
    averages: WeatherAverages
    scores: WeatherScores


@dataclass(frozen=True, slots=True)
class CitiesScores:
    """Represents the ranked weather score response for a date range."""

    start_date: date
    end_date: date
    cities: list[CityWeatherScore]
