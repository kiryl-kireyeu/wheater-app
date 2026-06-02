from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class CoordinatesResponse(BaseModel):
    latitude: float = Field(..., examples=[52.2297])
    longitude: float = Field(..., examples=[21.0122])


class WeatherAveragesResponse(BaseModel):
    temperature_2m: float = Field(..., description="Average 2m temperature in Celsius.")
    wind_speed_10m: float = Field(..., description="Average 10m wind speed in m/s.")
    relative_humidity_2m: float = Field(..., description="Average 2m relative humidity in %.")
    cloud_cover: float = Field(..., description="Average cloud cover in %.")

    model_config = ConfigDict(from_attributes=True)


class WeatherScoresResponse(BaseModel):
    temperature: float
    wind: float
    humidity: float
    cloud: float
    total: float

    model_config = ConfigDict(from_attributes=True)


class CityWeatherScoreResponse(BaseModel):
    rank: int
    city: str
    country: str
    coordinates: CoordinatesResponse
    averages: WeatherAveragesResponse
    scores: WeatherScoresResponse


class CitiesScoresResponse(BaseModel):
    start_date: date
    end_date: date
    cities: list[CityWeatherScoreResponse]
