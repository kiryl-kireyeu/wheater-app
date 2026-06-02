from datetime import date, timedelta

import pytest

from app.core.date_range import DateRange
from app.services.weather_scores.validation import validate_historical_range


def test_validate_historical_range_allows_yesterday() -> None:
    yesterday = date.today() - timedelta(days=1)

    validate_historical_range(DateRange(start_date=yesterday, end_date=yesterday))


def test_validate_historical_range_rejects_today() -> None:
    today = date.today()

    with pytest.raises(ValueError, match="yesterday"):
        validate_historical_range(DateRange(start_date=today, end_date=today))
