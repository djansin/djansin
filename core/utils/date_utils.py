"""Provides utility functions for date calculations in both Jalali and Gregorian calendars.

This module implements helper functions for converting between Jalali and Gregorian
calendars, calculating month/season/half-year boundaries, and working with date ranges.

IMPORTANT - What these functions provide:
    - Jalali calendar conversions to Gregorian datetime objects
    - Month start/end calculations for Jalali calendar
    - Half-year (semester) range calculations for both calendars
    - Season start detection for Jalali calendar
    - Current period detection (this half-year, this season)

All functions return timezone-aware datetime objects when appropriate, using
Django's current timezone for Gregorian functions.
"""

import jdatetime
from django.utils import timezone

from core.exceptions.app import InvalidHalfYearError, InvalidSeasonError


# ========== Jalali Calendar Functions ==========


def jalali_month_start(month: int, year: int | None = None) -> timezone.datetime:
    """Returns the first day of a given Jalali month as a Gregorian datetime.

    Args:
        month: Jalali month number (1-12, where 1 = Farvardin, 12 = Esfand).
        year: Jalali year (e.g., 1405). If None, uses current Jalali year.

    Returns:
        datetime: Gregorian datetime at midnight of the first day of the month.

    Examples:
        >>> jalali_month_start(1, 1405)
        datetime.datetime(2026, 3, 21, 0, 0)
    """
    if year is None:
        year = jdatetime.date.today().year

    tz = timezone.get_current_timezone()

    # Create first day of the month in Jalali calendar
    jalali_date: jdatetime.date = jdatetime.date(year, month, 1)
    gregorian_date = jalali_date.togregorian()

    gregorian_datetime: timezone.datetime = timezone.datetime(
        gregorian_date.year, gregorian_date.month, gregorian_date.day, tzinfo=tz
    )

    return gregorian_datetime


def jalali_month_end(month: int, year: int | None = None) -> timezone.datetime:
    """Returns the last day of a given Jalali month as a Gregorian datetime.

    Args:
        month: Jalali month number (1-12).
        year: Jalali year. If None, uses current Jalali year.

    Returns:
        datetime: Gregorian datetime at midnight of the last day of the month.

    Examples:
        >>> jalali_month_end(1, 1405)  # Last day of Farvardin
        datetime.datetime(2026, 4, 20, 0, 0)
    """
    if year is None:
        year = jdatetime.date.today().year

    tz = timezone.get_current_timezone()
    next_month_first: jdatetime.date

    # Get first day of next month, then subtract one day
    if month == 12:
        next_month_first = jdatetime.date(year + 1, 1, 1)
    else:
        next_month_first = jdatetime.date(year, month + 1, 1)

    gregorian_date = (next_month_first - timezone.timedelta(days=1)).togregorian()
    gregorian_datetime: timezone.datetime = timezone.datetime(
        gregorian_date.year, gregorian_date.month, gregorian_date.day, tzinfo=tz
    )

    return gregorian_datetime


def jalali_year_range(year: int) -> tuple[timezone.datetime, timezone.datetime]:
    """Returns the start and end datetimes for a Jalali year as Gregorian datetimes.

    Args:
        year: Jalali year (e.g., 1405).

    Returns:
        tuple[datetime, datetime]: (start_datetime, end_datetime) for the Jalali year,
            where start is Farvardin 1 at midnight and end is the last moment of
            Esfand 29/30 (depending on leap year).

    Examples:
        >>> start, end = jalali_year_range(1405)
        >>> start  # Farvardin 1, 1405
        datetime.datetime(2026, 3, 21, 0, 0)
        >>> end    # Last day of Esfand, 1405
        datetime.datetime(2027, 3, 20, 0, 0)

    Note:
        Jalali years start on Farvardin 1 (typically March 21) and end on
        Esfand 29 or 30 (typically March 20 of the next Gregorian year).
    """
    # Start: Farvardin 1
    start_date = jalali_month_start(1, year)
    # End: Last day of Esfand (month 12)
    end_date = jalali_month_end(12, year)

    return (start_date, end_date)


def jalali_half_year_range(
    half: int, year: int
) -> tuple[timezone.datetime, timezone.datetime]:
    """Returns the start and end datetimes for a Jalali half-year (semester).

    First half (half=1): Farvardin 1 to last day of Shahrivar (months 1-6)
    Second half (half=2): Mehr 1 to last day of Esfand (months 7-12)

    Args:
        half: Half-year number (1 or 2).
        year: Jalali year.

    Returns:
        tuple[datetime, datetime]: (start_datetime, end_datetime) for the half-year.

    Raises:
        InvalidHalfYearError: If half is not 1 or 2.

    Examples:
        >>> start, end = jalali_half_year_range(1, 1405)
        >>> start  # Farvardin 1, 1405
        datetime.datetime(2026, 3, 21, 0, 0)
        >>> end    # Last day of Shahrivar, 1405
        datetime.datetime(2026, 9, 21, 0, 0)
    """
    if half == 1:
        # Start: Farvardin 1
        start_date = jalali_month_start(1, year)
        # End: Last day of Shahrivar (month 6)
        end_date = jalali_month_end(6, year)
    elif half == 2:
        # Start: Mehr 1 (month 7)
        start_date = jalali_month_start(7, year)
        # End: Last day of Esfand (month 12)
        end_date = jalali_month_end(12, year)
    else:
        raise InvalidHalfYearError(half=half)

    return (start_date, end_date)


def jalali_season_start(season: int, year: int | None = None) -> timezone.datetime:
    """Returns the first day of a Jalali season as a Gregorian datetime.

    Seasons in Jalali calendar:
        1 = Spring (Farvardin, Ordibehesht, Khordad)    -> Farvardin 1
        2 = Summer (Tir, Mordad, Shahrivar)             -> Tir 1
        3 = Autumn (Mehr, Aban, Azar)                   -> Mehr 1
        4 = Winter (Dey, Bahman, Esfand)                -> Dey 1

    Args:
        season: Season number (1-4).
        year: Jalali year. If None, uses current Jalali year.

    Returns:
        datetime: Gregorian datetime of the first day of the season.

    Raises:
        InvalidSeasonError: If season is not between 1 and 4.

    Examples:
        >>> jalali_season_start(2, 1405)  # Start of Summer 1405
        datetime.datetime(2026, 6, 22, 0, 0)  # Tir 1, 1405
    """
    if year is None:
        year = jdatetime.date.today().year

    # First month of each season
    season_months = {
        1: 1,  # Spring -> Farvardin
        2: 4,  # Summer -> Tir
        3: 7,  # Autumn -> Mehr
        4: 10,  # Winter -> Dey
    }

    if season not in season_months:
        raise InvalidSeasonError(season=season)

    month = season_months[season]
    return jalali_month_start(month, year)


def this_jalali_season_started() -> timezone.datetime:
    """Returns the first day of the current Jalali season as a Gregorian datetime.

    Returns:
        datetime: Gregorian datetime of the first day of the current season.

    Examples:
        >>> # If today is 2026-07-15 (Mordad 1405 - Summer)
        >>> this_jalali_season_started()
        datetime.datetime(2026, 6, 22, 0, 0)  # Tir 1, 1405
    """
    today = jdatetime.date.today()
    # Calculate season: months 1-3 = 1, 4-6 = 2, 7-9 = 3, 10-12 = 4
    season = (today.month - 1) // 3 + 1
    return jalali_season_start(season, today.year)


def this_jalali_half_year() -> tuple[timezone.datetime, timezone.datetime]:
    """Returns the start and end datetimes for the current Jalali half-year.

    Determines whether today falls in the first or second half of the Jalali year
    and returns the corresponding range.

    Returns:
        tuple[datetime, datetime]: (start_datetime, end_datetime) for the current half-year.

    Examples:
        >>> # If today is in Farvardin (first half)
        >>> start, end = this_jalali_half_year()
        >>> start  # Farvardin 1 of current year
        >>> end    # Last day of Shahrivar of current year
    """
    today = jdatetime.date.today()

    # Determine which half of the year we're in
    # Months 1-6 = first half (half=1), months 7-12 = second half (half=2)
    half = 1 if today.month <= 6 else 2

    return jalali_half_year_range(half, today.year)


# ========== Gregorian Calendar Functions ==========


def gregorian_half_year_range(
    half: int, year: int
) -> tuple[timezone.datetime, timezone.datetime]:
    """Returns the start and end datetimes for a Gregorian half-year.

    Uses Django's current timezone for timezone-aware datetimes.

    First half (half=1): January 1 to June 30
    Second half (half=2): July 1 to December 31

    Args:
        half: Half-year number (1 or 2).
        year: Gregorian year.

    Returns:
        tuple[datetime, datetime]: (start_datetime, end_datetime) for the half-year,
            with timezone awareness.

    Raises:
        InvalidHalfYearError: If half is not 1 or 2.

    Examples:
        >>> start, end = gregorian_half_year_range(1, 2024)
        >>> start
        datetime.datetime(2024, 1, 1, 0, 0, tzinfo=...)
        >>> end
        datetime.datetime(2024, 6, 30, 23, 59, 59, 999999, tzinfo=...)
    """
    tz = timezone.get_current_timezone()

    if half == 1:
        start = timezone.datetime(year, 1, 1, 0, 0, 0, tzinfo=tz)
        end = timezone.datetime(year, 6, 30, 23, 59, 59, 999999, tzinfo=tz)
    elif half == 2:
        start = timezone.datetime(year, 7, 1, 0, 0, 0, tzinfo=tz)
        end = timezone.datetime(year, 12, 31, 23, 59, 59, 999999, tzinfo=tz)
    else:
        raise InvalidHalfYearError(half=half)

    return (start, end)


def gregorian_year_range(year: int) -> tuple[timezone.datetime, timezone.datetime]:
    """Returns the start and end datetimes for a Gregorian year.

    Uses Django's current timezone for timezone-aware datetimes.

    Args:
        year: Gregorian year.

    Returns:
        tuple[datetime, datetime]: (start_datetime, end_datetime) for the year.

    Examples:
        >>> start, end = gregorian_year_range(2024)
        >>> start
        datetime.datetime(2024, 1, 1, 0, 0, tzinfo=...)
        >>> end
        datetime.datetime(2024, 12, 31, 23, 59, 59, 999999, tzinfo=...)
    """
    tz = timezone.get_current_timezone()

    start = timezone.datetime(year, 1, 1, 0, 0, 0, tzinfo=tz)
    end = timezone.datetime(year, 12, 31, 23, 59, 59, 999999, tzinfo=tz)

    return (start, end)


def this_gregorian_half_year() -> tuple[int, int]:
    """Returns the current Gregorian half-year as (year, half).

    Determines the half based on the current month:
    - Months 1-6 = half 1
    - Months 7-12 = half 2

    Returns:
        tuple[int, int]: (year, half) where half is 1 or 2.

    Examples:
        >>> # If today is March 15, 2024
        >>> this_gregorian_half_year()
        (2024, 1)

        >>> # If today is August 20, 2024
        >>> this_gregorian_half_year()
        (2024, 2)
    """
    today = timezone.now().date()
    year = today.year
    half = 1 if today.month <= 6 else 2
    return (year, half)


def get_gregorian_half_year(date_time: timezone.datetime) -> tuple[int, int]:
    """Returns the Gregorian half-year for a given datetime.

    Args:
        date_time: The datetime to analyze.

    Returns:
        tuple[int, int]: (year, half) where half is 1 for Jan-Jun, 2 for Jul-Dec.
    """
    year = date_time.year
    half = 1 if date_time.month <= 6 else 2
    return (year, half)


def gregorian_half_year_from_string(semester: str) -> tuple[int, int]:
    """Parses a Gregorian half-year string into (year, half).

    Expected format: "YYYY-H" where H is 1 or 2 (e.g., "2024-1", "2024-2")

    Args:
        semester: Semester string in format "YYYY-H".

    Returns:
        tuple[int, int]: (year, half)

    Raises:
        InvalidHalfYearError: If the string format is invalid or half is not 1 or 2.

    Examples:
        >>> gregorian_half_year_from_string("2024-1")
        (2024, 1)

        >>> gregorian_half_year_from_string("2024-2")
        (2024, 2)
    """
    try:
        year_str, half_str = semester.split("-")
        year = int(year_str)
        half = int(half_str)

        if half not in (1, 2):
            raise InvalidHalfYearError(half=half)

        return (year, half)
    except (ValueError, IndexError) as e:
        raise InvalidHalfYearError(half=semester) from e
