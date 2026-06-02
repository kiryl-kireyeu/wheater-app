from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_weather_scores_service
from app.core.cities import CITIES
from app.core.date_range import DateRange
from app.main import app
from app.services.open_meteo import OpenMeteoError
from app.services.scoring import WeatherScores
from app.services.weather_scores import CitiesScores, CityWeatherScore, WeatherAverages


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> None:
    yield
    app.dependency_overrides.clear()


def test_cities_scores_endpoint_returns_ranked_response() -> None:
    fake_service = FakeWeatherScoresService(
        result=CitiesScores(
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 1),
            cities=[
                _city_score(rank=1, city_index=1, total=9.5),
                _city_score(rank=2, city_index=0, total=8.5),
            ],
        )
    )

    response = _client_with_service(fake_service).get(
        "/api/v1/cities-scores?start_date=2026-06-01&end_date=2026-06-01"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["start_date"] == "2026-06-01"
    assert payload["end_date"] == "2026-06-01"
    assert [city["city"] for city in payload["cities"]] == ["Gdansk", "Warsaw"]
    assert payload["cities"][0]["rank"] == 1
    assert payload["cities"][0]["scores"]["total"] == 9.5


def test_cities_scores_endpoint_defaults_to_yesterday() -> None:
    yesterday = date.today() - timedelta(days=1)
    fake_service = FakeWeatherScoresService(
        result=CitiesScores(
            start_date=yesterday,
            end_date=yesterday,
            cities=[],
        )
    )

    response = _client_with_service(fake_service).get("/api/v1/cities-scores")

    assert response.status_code == 200
    assert fake_service.last_date_range == DateRange(start_date=yesterday, end_date=yesterday)
    assert response.json()["start_date"] == yesterday.isoformat()
    assert response.json()["end_date"] == yesterday.isoformat()


def test_cities_scores_endpoint_rejects_start_date_after_end_date() -> None:
    fake_service = FakeWeatherScoresService(
        result=CitiesScores(start_date=date(2026, 6, 1), end_date=date(2026, 6, 1), cities=[])
    )

    response = _client_with_service(fake_service).get(
        "/api/v1/cities-scores?start_date=2026-06-02&end_date=2026-06-01"
    )

    assert response.status_code == 422
    assert "start_date" in response.json()["detail"]


def test_cities_scores_endpoint_maps_weather_errors_to_bad_gateway() -> None:
    response = _client_with_service(FailingWeatherScoresService()).get("/api/v1/cities-scores")

    assert response.status_code == 502
    assert "Open-Meteo" in response.json()["detail"]


def test_cities_scores_endpoint_is_documented_in_openapi_schema() -> None:
    response = TestClient(app).get("/openapi.json")

    assert response.status_code == 200
    operation = response.json()["paths"]["/api/v1/cities-scores"]["get"]
    assert operation["summary"] == "Get ranked city weather scores"
    assert [parameter["name"] for parameter in operation["parameters"]] == [
        "start_date",
        "end_date",
    ]


class FakeWeatherScoresService:
    def __init__(self, result: CitiesScores) -> None:
        self._result = result
        self.last_date_range: DateRange | None = None

    async def get_cities_scores(self, date_range: DateRange) -> CitiesScores:
        self.last_date_range = date_range
        return self._result


class FailingWeatherScoresService:
    async def get_cities_scores(self, date_range: DateRange) -> CitiesScores:
        raise OpenMeteoError("Open-Meteo request failed.")


def _client_with_service(service: object) -> TestClient:
    app.dependency_overrides[get_weather_scores_service] = lambda: service
    return TestClient(app)


def _city_score(rank: int, city_index: int, total: float) -> CityWeatherScore:
    return CityWeatherScore(
        rank=rank,
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
