from datetime import date

import pytest

from app.core.date_range import resolve_date_range


def test_resolve_date_range_defaults_to_yesterday() -> None:
    date_range = resolve_date_range(today=date(2026, 6, 2))

    assert date_range.start_date == date(2026, 6, 1)
    assert date_range.end_date == date(2026, 6, 1)


def test_resolve_date_range_uses_single_start_date_as_one_day_range() -> None:
    date_range = resolve_date_range(start_date=date(2026, 5, 30))

    assert date_range.start_date == date(2026, 5, 30)
    assert date_range.end_date == date(2026, 5, 30)


def test_resolve_date_range_uses_single_end_date_as_one_day_range() -> None:
    date_range = resolve_date_range(end_date=date(2026, 5, 30))

    assert date_range.start_date == date(2026, 5, 30)
    assert date_range.end_date == date(2026, 5, 30)


def test_resolve_date_range_rejects_start_after_end() -> None:
    with pytest.raises(ValueError, match="start_date"):
        resolve_date_range(start_date=date(2026, 6, 2), end_date=date(2026, 6, 1))
