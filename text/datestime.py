"""English date, time, and quarter normalization for TTS."""

import re
import calendar
import inflect

_inflect = inflect.engine()

# --- Date: MM/DD/YYYY ---
_date_re = re.compile(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b')

# --- Date Range: MM/DD1-DD2/YYYY ---
_date_range_re = re.compile(r'\b(\d{1,2})/(\d{1,2})-(\d{1,2})/(\d{4})\b')

# --- Time with AM/PM: 10:00 AM, 3:05PM ---
_time_ampm_re = re.compile(
    r'\b(\d{1,2}):(\d{2})\s*([AaPp]\.?\s*[Mm]\.?)\b')

# --- Time 24h without AM/PM: 14:30 (only when not already matched by ampm) ---
_time_24h_re = re.compile(
    r'(?<![/\d])(\d{1,2}):(\d{2})(?!\s*[AaPp]\.?\s*[Mm])(?!\s*\d)')

# --- Quarter: Q1 2026, Q3/2026 ---
_quarter_re = re.compile(r'\bQ([1-4])[\s/]+(\d{4})\b', re.IGNORECASE)

_ordinal_map = {1: 'first', 2: 'second', 3: 'third', 4: 'fourth'}


def _expand_year(year):
    """Convert a 4-digit year to spoken English words.

    Examples:
        2000 -> 'two thousand'
        2005 -> 'two thousand five'
        2026 -> 'twenty twenty six'
        1999 -> 'nineteen ninety nine'
        1900 -> 'nineteen hundred'
    """
    if year == 2000:
        return 'two thousand'
    elif 2001 <= year <= 2009:
        ones = _inflect.number_to_words(year % 100)
        return 'two thousand ' + ones.replace('-', ' ')
    elif year % 100 == 0 and 1000 < year < 10000:
        century = _inflect.number_to_words(year // 100)
        return century.replace('-', ' ') + ' hundred'
    elif 1000 < year < 10000:
        first = _inflect.number_to_words(year // 100)
        second_num = year % 100
        if second_num < 10:
            second = 'oh ' + _inflect.number_to_words(second_num)
        else:
            second = _inflect.number_to_words(second_num)
        return (first + ' ' + second).replace('-', ' ')
    else:
        return _inflect.number_to_words(year, andword='').replace('-', ' ').replace(',', '')


def _expand_date(m):
    """Expand MM/DD/YYYY to 'month day_ordinal, year_words'.

    Validates that month is 1-12 and day is 1-31.
    """
    month = int(m.group(1))
    day = int(m.group(2))
    year = int(m.group(3))

    if not (1 <= month <= 12 and 1 <= day <= 31):
        return m.group(0)

    month_name = calendar.month_name[month].lower()
    day_ordinal = _inflect.ordinal(_inflect.number_to_words(day)).replace('-', ' ')
    year_words = _expand_year(year)
    return f"{month_name} {day_ordinal}, {year_words}"


def _expand_time_ampm(m):
    """Expand '10:30 AM' to 'ten thirty a m'."""
    hour = int(m.group(1))
    minute = int(m.group(2))
    ampm_raw = m.group(3)

    if not (1 <= hour <= 12 and 0 <= minute <= 59):
        return m.group(0)

    hour_word = _inflect.number_to_words(hour).replace('-', ' ')
    if minute == 0:
        minute_word = ''
    elif minute < 10:
        minute_word = ' oh ' + _inflect.number_to_words(minute)
    else:
        minute_word = ' ' + _inflect.number_to_words(minute).replace('-', ' ')

    ampm_clean = ampm_raw.lower().replace('.', '').replace(' ', '')
    ampm_word = ' a m' if ampm_clean == 'am' else ' p m'

    return hour_word + minute_word + ampm_word


def _expand_time_24h(m):
    """Expand '14:30' to 'fourteen thirty'."""
    hour = int(m.group(1))
    minute = int(m.group(2))

    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return m.group(0)

    hour_word = _inflect.number_to_words(hour).replace('-', ' ')
    if minute == 0:
        minute_word = ''
    elif minute < 10:
        minute_word = ' oh ' + _inflect.number_to_words(minute)
    else:
        minute_word = ' ' + _inflect.number_to_words(minute).replace('-', ' ')

    return hour_word + minute_word


def _expand_quarter(m):
    """Expand 'Q3 2026' to 'third quarter twenty twenty six'."""
    quarter = int(m.group(1))
    year = int(m.group(2))
    quarter_word = _ordinal_map[quarter]
    year_words = _expand_year(year)
    return f"{quarter_word} quarter {year_words}"


def _expand_date_range(m):
    """Expand MM/DD1-DD2/YYYY to 'month day1_ordinal to day2_ordinal, year_words'.
    """
    month = int(m.group(1))
    day1 = int(m.group(2))
    day2 = int(m.group(3))
    year = int(m.group(4))

    if not (1 <= month <= 12 and 1 <= day1 <= 31 and 1 <= day2 <= 31):
        return m.group(0)

    month_name = calendar.month_name[month].lower()
    day1_ordinal = _inflect.ordinal(_inflect.number_to_words(day1)).replace('-', ' ')
    day2_ordinal = _inflect.ordinal(_inflect.number_to_words(day2)).replace('-', ' ')
    year_words = _expand_year(year)
    return f"{month_name} {day1_ordinal} to {day2_ordinal}, {year_words}"


def normalize_datestime(text):
    """Normalize dates, times, and quarters in English text.

    Processing order matters: dates first (to avoid partial matches with times),
    then AM/PM times, then 24h times, then quarters.
    """
    text = re.sub(_date_range_re, _expand_date_range, text)
    text = re.sub(_date_re, _expand_date, text)
    text = re.sub(_time_ampm_re, _expand_time_ampm, text)
    text = re.sub(_time_24h_re, _expand_time_24h, text)
    text = re.sub(_quarter_re, _expand_quarter, text)
    return text
