from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_weather_scores_service
from app.api.v1.cities_scores_presenter import to_cities_scores_response
from app.core.date_range import resolve_date_range
from app.schemas.weather import CitiesScoresResponse
from app.services.open_meteo import OpenMeteoError
from app.services.weather_scores import WeatherScoresService

router = APIRouter(prefix="/api/v1", tags=["weather scores"])


@router.get(
    "/cities-scores",
    response_model=CitiesScoresResponse,
    summary="Get ranked city weather scores",
    description="Returns selected cities sorted from best to worst weather score.",
)
async def get_cities_scores(
    service: Annotated[WeatherScoresService, Depends(get_weather_scores_service)],
    start_date: Annotated[
        date | None,
        Query(description="Start date in YYYY-MM-DD format. Defaults to yesterday."),
    ] = None,
    end_date: Annotated[
        date | None,
        Query(description="End date in YYYY-MM-DD format. Defaults to yesterday."),
    ] = None,
) -> CitiesScoresResponse:
    """Handle city weather score requests and map service errors to API responses."""
    try:
        date_range = resolve_date_range(start_date=start_date, end_date=end_date)
        scores = await service.get_cities_scores(date_range=date_range)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    except OpenMeteoError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return to_cities_scores_response(scores=scores)
