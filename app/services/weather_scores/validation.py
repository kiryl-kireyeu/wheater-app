from datetime import date, timedelta

from app.core.date_range import DateRange


def validate_historical_range(date_range: DateRange) -> None:
    """Validate that the requested range can be served by historical data."""
    yesterday = date.today() - timedelta(days=1)
    if date_range.end_date > yesterday:
        msg = "end_date must not be later than yesterday."
        raise ValueError(msg)
