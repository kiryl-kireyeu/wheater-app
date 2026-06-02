from dataclasses import dataclass

MIN_SCORE = 0.0
MAX_SCORE = 10.0

TEMPERATURE_TARGET_CELSIUS = 24.0
HUMIDITY_TARGET_PERCENT = 50.0
CLOUD_COVER_TARGET_PERCENT = 25.0

TEMPERATURE_WEIGHT = 0.35
WIND_SPEED_WEIGHT = 0.20
HUMIDITY_WEIGHT = 0.20
CLOUD_COVER_WEIGHT = 0.25


@dataclass(frozen=True, slots=True)
class WeatherScores:
    """Stores component weather scores and the weighted total score."""

    temperature: float
    wind: float
    humidity: float
    cloud: float
    total: float


def calculate_temperature_score(temperature_2m: float) -> float:
    """Calculate temperature score using 24°C as the ideal value."""
    score = MAX_SCORE - abs(temperature_2m - TEMPERATURE_TARGET_CELSIUS)
    return _round_score(_clamp_score(score))


def calculate_wind_score(wind_speed_10m: float) -> float:
    """Calculate wind score where lower wind speed is better."""
    score = MAX_SCORE - wind_speed_10m
    return _round_score(_clamp_score(score))


def calculate_humidity_score(relative_humidity_2m: float) -> float:
    """Calculate humidity score using 50% as the ideal value."""
    score = MAX_SCORE - abs(relative_humidity_2m - HUMIDITY_TARGET_PERCENT) / 5
    return _round_score(_clamp_score(score))


def calculate_cloud_score(cloud_cover: float) -> float:
    """Calculate cloud cover score using 25% as the ideal value."""
    if cloud_cover <= CLOUD_COVER_TARGET_PERCENT:
        score = cloud_cover / CLOUD_COVER_TARGET_PERCENT * MAX_SCORE
    else:
        score = (100 - cloud_cover) / (100 - CLOUD_COVER_TARGET_PERCENT) * MAX_SCORE

    return _round_score(_clamp_score(score))


def calculate_weather_scores(
    *,
    temperature_2m: float,
    wind_speed_10m: float,
    relative_humidity_2m: float,
    cloud_cover: float,
) -> WeatherScores:
    """Calculate component scores and weighted total weather score."""
    temperature = calculate_temperature_score(temperature_2m)
    wind = calculate_wind_score(wind_speed_10m)
    humidity = calculate_humidity_score(relative_humidity_2m)
    cloud = calculate_cloud_score(cloud_cover)
    total = (
        temperature * TEMPERATURE_WEIGHT
        + wind * WIND_SPEED_WEIGHT
        + humidity * HUMIDITY_WEIGHT
        + cloud * CLOUD_COVER_WEIGHT
    )

    return WeatherScores(
        temperature=temperature,
        wind=wind,
        humidity=humidity,
        cloud=cloud,
        total=_round_score(total),
    )


def _clamp_score(score: float) -> float:
    """Clamp a score to the supported 0-10 range."""
    return max(MIN_SCORE, min(MAX_SCORE, score))


def _round_score(score: float) -> float:
    """Round score values for stable API responses."""
    return round(score, 2)
