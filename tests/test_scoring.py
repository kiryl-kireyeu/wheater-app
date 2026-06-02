import pytest

from app.services.scoring import (
    calculate_cloud_score,
    calculate_humidity_score,
    calculate_temperature_score,
    calculate_weather_scores,
    calculate_wind_score,
)


def test_temperature_score_is_best_at_24_celsius() -> None:
    assert calculate_temperature_score(24) == 10


def test_temperature_score_decreases_by_one_per_degree_deviation() -> None:
    assert calculate_temperature_score(21.5) == 7.5
    assert calculate_temperature_score(27) == 7


def test_temperature_score_cannot_go_below_zero() -> None:
    assert calculate_temperature_score(40) == 0


def test_wind_score_is_best_at_zero_and_decreases_with_speed() -> None:
    assert calculate_wind_score(0) == 10
    assert calculate_wind_score(3.25) == 6.75
    assert calculate_wind_score(15) == 0


@pytest.mark.parametrize(
    ("humidity", "expected_score"),
    [
        (50, 10),
        (0, 0),
        (100, 0),
        (60, 8),
        (35, 7),
    ],
)
def test_humidity_score_uses_50_percent_as_target(
    humidity: float,
    expected_score: float,
) -> None:
    assert calculate_humidity_score(humidity) == expected_score


@pytest.mark.parametrize(
    ("cloud_cover", "expected_score"),
    [
        (25, 10),
        (0, 0),
        (100, 0),
        (12.5, 5),
        (62.5, 5),
    ],
)
def test_cloud_score_uses_25_percent_as_target(
    cloud_cover: float,
    expected_score: float,
) -> None:
    assert calculate_cloud_score(cloud_cover) == expected_score


def test_weather_scores_use_required_weights() -> None:
    scores = calculate_weather_scores(
        temperature_2m=24,
        wind_speed_10m=0,
        relative_humidity_2m=50,
        cloud_cover=25,
    )

    assert scores.temperature == 10
    assert scores.wind == 10
    assert scores.humidity == 10
    assert scores.cloud == 10
    assert scores.total == 10


def test_weather_scores_return_weighted_total() -> None:
    scores = calculate_weather_scores(
        temperature_2m=22,
        wind_speed_10m=4,
        relative_humidity_2m=60,
        cloud_cover=62.5,
    )

    assert scores.temperature == 8
    assert scores.wind == 6
    assert scores.humidity == 8
    assert scores.cloud == 5
    assert scores.total == 6.85
