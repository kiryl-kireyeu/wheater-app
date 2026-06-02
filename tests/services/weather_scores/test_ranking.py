from app.core.cities import CITIES
from app.services.scoring import WeatherScores
from app.services.weather_scores import CityWeatherScore, WeatherAverages
from app.services.weather_scores.ranking import rank_city_scores


def test_rank_city_scores_sorts_by_total_descending() -> None:
    ranked_scores = rank_city_scores(
        [
            _city_score(city_index=0, total=5),
            _city_score(city_index=1, total=9),
        ]
    )

    assert [city_score.city.name for city_score in ranked_scores] == ["Gdansk", "Warsaw"]
    assert [city_score.rank for city_score in ranked_scores] == [1, 2]


def test_rank_city_scores_preserves_input_order_for_equal_scores() -> None:
    ranked_scores = rank_city_scores(
        [
            _city_score(city_index=0, total=10),
            _city_score(city_index=1, total=10),
        ]
    )

    assert [city_score.city.name for city_score in ranked_scores] == ["Warsaw", "Gdansk"]


def _city_score(city_index: int, total: float) -> CityWeatherScore:
    return CityWeatherScore(
        rank=0,
        city=CITIES[city_index],
        averages=WeatherAverages(
            temperature_2m=24,
            wind_speed_10m=0,
            relative_humidity_2m=50,
            cloud_cover=25,
        ),
        scores=WeatherScores(
            temperature=10,
            wind=10,
            humidity=10,
            cloud=10,
            total=total,
        ),
    )
