from app.schemas.weather import (
    CitiesScoresResponse,
    CityWeatherScoreResponse,
    CoordinatesResponse,
    WeatherAveragesResponse,
    WeatherScoresResponse,
)
from app.services.weather_scores import CitiesScores


def to_cities_scores_response(scores: CitiesScores) -> CitiesScoresResponse:
    """Convert domain weather scores into the public API response schema."""
    # Keep this mapping at the API boundary so domain dataclasses stay framework-agnostic.
    return CitiesScoresResponse(
        start_date=scores.start_date,
        end_date=scores.end_date,
        cities=[
            CityWeatherScoreResponse(
                rank=city_score.rank,
                city=city_score.city.name,
                country=city_score.city.country,
                coordinates=CoordinatesResponse(
                    latitude=city_score.city.latitude,
                    longitude=city_score.city.longitude,
                ),
                averages=WeatherAveragesResponse.model_validate(city_score.averages),
                scores=WeatherScoresResponse.model_validate(city_score.scores),
            )
            for city_score in scores.cities
        ],
    )
