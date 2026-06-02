from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True, slots=True)
class DateRange:
    start_date: date
    end_date: date


def resolve_date_range(
    start_date: date | None = None,
    end_date: date | None = None,
    today: date | None = None,
) -> DateRange:
    """Resolve optional query dates into a validated date range.

    Defaults to yesterday when both dates are omitted. If only one boundary is
    provided, it is treated as a one-day range.
    """
    current_date = today or date.today()
    yesterday = current_date - timedelta(days=1)

    if start_date is None and end_date is None:
        return DateRange(start_date=yesterday, end_date=yesterday)

    resolved_start_date = start_date or end_date
    resolved_end_date = end_date or start_date

    if resolved_start_date is None or resolved_end_date is None:
        msg = "Date range could not be resolved."
        raise ValueError(msg)

    if resolved_start_date > resolved_end_date:
        msg = "start_date must be less than or equal to end_date."
        raise ValueError(msg)

    return DateRange(start_date=resolved_start_date, end_date=resolved_end_date)
