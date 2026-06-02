from app.services.weather_scores.schemas import CityWeatherScore


def rank_city_scores(city_scores: list[CityWeatherScore]) -> list[CityWeatherScore]:
    """Create the final ranked list sorted by total score descending."""
    sorted_city_scores = sorted(
        city_scores,
        key=lambda city_score: city_score.scores.total,
        reverse=True,
    )

    # Python sorting is stable, so equal scores keep the configured city order.
    return [
        CityWeatherScore(
            rank=index,
            city=city_score.city,
            averages=city_score.averages,
            scores=city_score.scores,
        )
        for index, city_score in enumerate(sorted_city_scores, start=1)
    ]
