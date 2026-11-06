"""Host-side tests for dish_genie_logic (CPython + pytest)."""

import pytest

from dish_genie_logic import (
    finish_time_display,
    format_time_display,
    seconds_to_duration_hh_mm,
)


@pytest.mark.parametrize(
    "amount,expected",
    [
        (0, "0:00"),
        (59, "0:00"),
        (60, "0:01"),
        (3600, "1:00"),
        (3661, "1:01"),
        (86399, "23:59"),
        (86400, "0:00"),
    ],
)
def test_seconds_to_duration_hh_mm(amount, expected):
    assert seconds_to_duration_hh_mm(amount) == expected


@pytest.mark.parametrize(
    "hour,minute,fmt,expected",
    [
        (14, 30, "24", "14:30"),
        (0, 5, "24", "00:05"),
        (14, 30, "12", "2:30 PM"),
        (0, 15, "12", "12:15 AM"),
        # Noon is ambiguous in the legacy branch logic (stays AM); assert actual behavior.
        (12, 0, "12", "12:0 AM"),
    ],
)
def test_format_time_display(hour, minute, fmt, expected):
    assert format_time_display(hour, minute, fmt) == expected


def test_finish_time_display_24h_adds_duration():
    # 10:00 + 1h30m => 11:30
    assert finish_time_display(10, 0, 5400, "24") == "11:30"


def test_finish_time_display_12h_cross_noon():
    # 11:00 + 2h => 1:0 PM (matches existing display behavior)
    assert finish_time_display(11, 0, 7200, "12") == "1:0 PM"
