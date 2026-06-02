from datetime import date
from typing import Any

from app.core.cities import City
from app.core.date_range import DateRange
from app.services.open_meteo.exceptions import OpenMeteoError
from app.services.open_meteo.schemas import HourlyWeatherData

HOURLY_VARIABLES = (
    "temperature_2m",
    "wind_speed_10m",
    "relative_humidity_2m",
    "cloud_cover",
)


def build_weather_params(city: City, date_range: DateRange) -> dict[str, str | float]:
    """Build Open-Meteo query parameters with explicit units and hourly metrics."""
    return build_weather_params_for_cities(cities=(city,), date_range=date_range)


def build_weather_params_for_cities(
    cities: tuple[City, ...],
    date_range: DateRange,
) -> dict[str, str | float]:
    """Build Open-Meteo query parameters for one batch request across cities."""
    return {
        "latitude": ",".join(str(city.latitude) for city in cities),
        "longitude": ",".join(str(city.longitude) for city in cities),
        "start_date": _format_date(date_range.start_date),
        "end_date": _format_date(date_range.end_date),
        "hourly": ",".join(HOURLY_VARIABLES),
        "wind_speed_unit": "ms",
        "timezone": "auto",
    }


def parse_hourly_weather(payload: dict[str, Any], city: City) -> HourlyWeatherData:
    """Parse and validate the hourly section returned by Open-Meteo."""
    hourly = payload.get("hourly")
    if not isinstance(hourly, dict):
        msg = f"Open-Meteo response for {city.name} does not contain hourly data."
        raise OpenMeteoError(msg)

    times = hourly.get("time")
    if not isinstance(times, list) or not times or not all(isinstance(item, str) for item in times):
        msg = f"Open-Meteo response for {city.name} contains invalid hourly timestamps."
        raise OpenMeteoError(msg)

    return HourlyWeatherData(
        time=times,
        temperature_2m=_extract_numeric_series(hourly, "temperature_2m", city, len(times)),
        wind_speed_10m=_extract_numeric_series(hourly, "wind_speed_10m", city, len(times)),
        relative_humidity_2m=_extract_numeric_series(
            hourly,
            "relative_humidity_2m",
            city,
            len(times),
        ),
        cloud_cover=_extract_numeric_series(hourly, "cloud_cover", city, len(times)),
    )


def parse_hourly_weather_list(
    payload: dict[str, Any] | list[Any], cities: tuple[City, ...]
) -> list[HourlyWeatherData]:
    """Parse Open-Meteo batch response preserving the configured city order."""
    if len(cities) == 1 and isinstance(payload, dict):
        return [parse_hourly_weather(payload=payload, city=cities[0])]

    if not isinstance(payload, list):
        msg = "Open-Meteo batch response is not a list."
        raise OpenMeteoError(msg)

    if len(payload) != len(cities):
        msg = "Open-Meteo batch response length does not match requested cities."
        raise OpenMeteoError(msg)

    parsed_results: list[HourlyWeatherData] = []
    for city, city_payload in zip(cities, payload, strict=True):
        if not isinstance(city_payload, dict):
            msg = f"Open-Meteo batch response for {city.name} is not an object."
            raise OpenMeteoError(msg)
        parsed_results.append(parse_hourly_weather(payload=city_payload, city=city))

    return parsed_results


def _extract_numeric_series(
    hourly: dict[str, Any],
    key: str,
    city: City,
    expected_length: int,
) -> list[float]:
    """Extract one non-empty numeric hourly series from an Open-Meteo response."""
    values = hourly.get(key)
    if not isinstance(values, list):
        msg = f"Open-Meteo response for {city.name} is missing {key}."
        raise OpenMeteoError(msg)

    if len(values) != expected_length:
        msg = f"Open-Meteo response for {city.name} contains mismatched {key} length."
        raise OpenMeteoError(msg)

    numeric_values: list[float] = []
    for value in values:
        if value is None:
            continue

        if isinstance(value, bool) or not isinstance(value, int | float):
            msg = f"Open-Meteo response for {city.name} contains invalid {key} values."
            raise OpenMeteoError(msg)

        numeric_values.append(float(value))

    if not numeric_values:
        msg = f"Open-Meteo response for {city.name} contains no usable {key} values."
        raise OpenMeteoError(msg)

    return numeric_values


def _format_date(value: date) -> str:
    """Format dates as Open-Meteo ISO date query values."""
    return value.isoformat()
