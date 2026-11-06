"""
Host-testable helpers for Dish Genie (timer display math).

CircuitPython `code.py` imports this module; keep imports stdlib-only here
so pytest can run on CPython in CI.
"""


def seconds_to_duration_hh_mm(amount: float) -> str:
    """Convert a duration in seconds to 'H:MM' (hours may exceed 24)."""
    seconds = float(amount) % (24 * 3600)
    hour = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    return "%d:%02d" % (hour, minutes)


def format_time_display(hour: int, minute: int, hour_format: str) -> str:
    """
    Format a wall-clock time for display (12h or 24h).

    Matches the behavior of the former Timer._format_time implementation
    (including minute carry and single-digit handling).
    """
    minute_str = str(minute)
    if len(minute_str) < 2:
        minute = int(f"0{minute_str}")

    if minute > 60:
        minute -= 60
        hour += 1

    if hour_format == "12":
        am_pm = "AM"
        display_hour = hour
        if hour == 0:
            display_hour = 12
        elif hour > 12:
            am_pm = "PM"
            display_hour = hour - 12
        return f"{display_hour}:{minute} {am_pm}"
    return f"{hour:02d}:{minute:02d}"


def finish_time_display(
    start_hour: int,
    start_min: int,
    duration_seconds: float,
    hour_format: str,
) -> str:
    """End time after adding duration to start, using the same rules as the device."""
    timer_time = seconds_to_duration_hh_mm(duration_seconds)
    timer_hour = int(timer_time.split(":")[0])
    timer_min = int(timer_time.split(":")[1])
    finish_hour = start_hour + timer_hour
    finish_min = start_min + timer_min
    return format_time_display(finish_hour, finish_min, hour_format)
