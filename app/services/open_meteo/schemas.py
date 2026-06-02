from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HourlyWeatherData:
    time: list[str]
    temperature_2m: list[float]
    wind_speed_10m: list[float]
    relative_humidity_2m: list[float]
    cloud_cover: list[float]
