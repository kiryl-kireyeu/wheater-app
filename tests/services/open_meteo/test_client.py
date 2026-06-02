import asyncio
import json
from collections.abc import Awaitable, Callable
from datetime import date

import httpx
import pytest

from app.core.cities import CITIES
from app.core.date_range import DateRange
from app.services.open_meteo import OpenMeteoClient, OpenMeteoError


def test_fetch_hourly_weather_builds_expected_request_params() -> None:
    captured_request: httpx.Request | None = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json=_open_meteo_payload())

    weather_data = _fetch_with_handler(handler)

    assert captured_request is not None
    assert captured_request.url.params["latitude"] == str(CITIES[0].latitude)
    assert captured_request.url.params["longitude"] == str(CITIES[0].longitude)
    assert captured_request.url.params["start_date"] == "2026-06-01"
    assert captured_request.url.params["end_date"] == "2026-06-01"
    assert captured_request.url.params["hourly"] == (
        "temperature_2m,wind_speed_10m,relative_humidity_2m,cloud_cover"
    )
    assert captured_request.url.params["wind_speed_unit"] == "ms"
    assert captured_request.url.params["timezone"] == "auto"
    assert weather_data.temperature_2m == [24.0, 25.0]


def test_fetch_hourly_weather_parses_required_hourly_data() -> None:
    weather_data = _fetch_with_handler(lambda _: httpx.Response(200, json=_open_meteo_payload()))

    assert weather_data.time == ["2026-06-01T00:00", "2026-06-01T01:00"]
    assert weather_data.temperature_2m == [24.0, 25.0]
    assert weather_data.wind_speed_10m == [1.0, 2.0]
    assert weather_data.relative_humidity_2m == [50.0, 55.0]
    assert weather_data.cloud_cover == [25.0, 30.0]


def test_fetch_hourly_weather_ignores_null_metric_values() -> None:
    payload = _open_meteo_payload()
    payload["hourly"]["temperature_2m"] = [None, 24]

    weather_data = _fetch_with_handler(lambda _: httpx.Response(200, json=payload))

    assert weather_data.temperature_2m == [24.0]


@pytest.mark.parametrize("status_code", [400, 500])
def test_fetch_hourly_weather_raises_for_http_errors(status_code: int) -> None:
    with pytest.raises(OpenMeteoError, match=f"HTTP {status_code}"):
        _fetch_with_handler(lambda _: httpx.Response(status_code, json={"reason": "error"}))


def test_fetch_hourly_weather_raises_for_network_errors() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection failed", request=request)

    with pytest.raises(OpenMeteoError, match="request failed"):
        _fetch_with_handler(handler)


def test_fetch_hourly_weather_raises_for_invalid_json() -> None:
    with pytest.raises(OpenMeteoError, match="invalid JSON"):
        _fetch_with_handler(lambda _: httpx.Response(200, content=b"not-json"))


def test_fetch_hourly_weather_raises_for_non_object_json() -> None:
    with pytest.raises(OpenMeteoError, match="invalid JSON object"):
        _fetch_with_handler(lambda _: httpx.Response(200, json=[]))


def test_fetch_hourly_weather_raises_when_hourly_data_is_missing() -> None:
    with pytest.raises(OpenMeteoError, match="hourly data"):
        _fetch_with_handler(lambda _: httpx.Response(200, json={}))


@pytest.mark.parametrize(
    "time_value",
    [
        [],
        [1],
        "2026-06-01T00:00",
    ],
)
def test_fetch_hourly_weather_raises_when_timestamps_are_invalid(time_value: object) -> None:
    payload = _open_meteo_payload()
    payload["hourly"]["time"] = time_value

    with pytest.raises(OpenMeteoError, match="timestamps"):
        _fetch_with_handler(lambda _: httpx.Response(200, json=payload))


def test_fetch_hourly_weather_raises_when_required_metric_is_missing() -> None:
    payload = _open_meteo_payload()
    del payload["hourly"]["cloud_cover"]

    with pytest.raises(OpenMeteoError, match="cloud_cover"):
        _fetch_with_handler(lambda _: httpx.Response(200, json=payload))


def test_fetch_hourly_weather_raises_when_metric_values_are_not_numeric() -> None:
    payload = _open_meteo_payload()
    payload["hourly"]["wind_speed_10m"] = ["bad-value"]

    with pytest.raises(OpenMeteoError, match="wind_speed_10m"):
        _fetch_with_handler(lambda _: httpx.Response(200, json=payload))


def test_fetch_hourly_weather_raises_when_metric_values_are_boolean() -> None:
    payload = _open_meteo_payload()
    payload["hourly"]["wind_speed_10m"] = [True]

    with pytest.raises(OpenMeteoError, match="wind_speed_10m"):
        _fetch_with_handler(lambda _: httpx.Response(200, json=payload))


def test_fetch_hourly_weather_raises_when_metric_values_are_empty() -> None:
    payload = _open_meteo_payload()
    payload["hourly"]["temperature_2m"] = []

    with pytest.raises(OpenMeteoError, match="temperature_2m"):
        _fetch_with_handler(lambda _: httpx.Response(200, json=payload))


def test_fetch_hourly_weather_raises_when_metric_values_are_all_null() -> None:
    payload = _open_meteo_payload()
    payload["hourly"]["temperature_2m"] = [None, None]

    with pytest.raises(OpenMeteoError, match="temperature_2m"):
        _fetch_with_handler(lambda _: httpx.Response(200, json=payload))


def _fetch_with_handler(
    handler: Callable[[httpx.Request], httpx.Response | Awaitable[httpx.Response]],
) -> object:
    transport = httpx.MockTransport(handler)
    date_range = DateRange(start_date=date(2026, 6, 1), end_date=date(2026, 6, 1))

    async def run() -> object:
        async with httpx.AsyncClient(transport=transport) as http_client:
            return await OpenMeteoClient(http_client=http_client).fetch_hourly_weather(
                city=CITIES[0],
                date_range=date_range,
            )

    return asyncio.run(run())


def _open_meteo_payload() -> dict[str, object]:
    return json.loads(
        """
        {
          "hourly": {
            "time": ["2026-06-01T00:00", "2026-06-01T01:00"],
            "temperature_2m": [24, 25],
            "wind_speed_10m": [1, 2],
            "relative_humidity_2m": [50, 55],
            "cloud_cover": [25, 30]
          }
        }
        """
    )
