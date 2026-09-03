"""Expand mixed letter-number sequences, measurement units, dimensions,
compound units, and temperature for English TTS normalization."""

import re

# ============================================================
# Measurement units
# ============================================================

# Build regex from the key dict — sorted longest-first so 'ghz' matches before 'hz'
_hardware_key = {
    # Storage
    'tb': 'terabyte', 'gb': 'gigabyte', 'mb': 'megabyte', 'kb': 'kilobyte',
    # Frequency
    'ghz': 'gigahertz', 'mhz': 'megahertz', 'khz': 'kilohertz', 'hz': 'hertz',
    # Length — metric
    'nm': 'nanometer', 'mm': 'millimeter', 'cm': 'centimeter',
    'dm': 'decimeter', 'km': 'kilometer',
    # Length — imperial
    'ft': 'foot', 'yd': 'yard', 'mi': 'mile',
    # Weight — metric
    'kg': 'kilogram', 'mg': 'milligram',
    # Weight — imperial
    'lb': 'pound', 'oz': 'ounce',
    # Volume
    'ml': 'milliliter', 'gal': 'gallon',
    # Speed / consumption (compound phrases — not pluralized)
    'mph': 'miles per hour', 'mpg': 'miles per gallon',
}

_irregular_plurals = {
    'foot': 'feet',
}

# Sort unit keys longest-first, then build the alternation
_unit_keys_sorted = sorted(_hardware_key.keys(), key=len, reverse=True)
_hardware_re = re.compile(
    r'([0-9]+(?:[.,][0-9]+)?)(?:\s?)'
    r'(' + '|'.join(_unit_keys_sorted) + r')\b',
    re.IGNORECASE,
)


# ============================================================
# Area and volume: m2, km², ft³, cm3, etc.
# ============================================================

_area_volume_base = {
    'km': 'kilometer', 'm': 'meter', 'cm': 'centimeter', 'mm': 'millimeter',
    'ft': 'foot', 'mi': 'mile', 'yd': 'yard', 'in': 'inch',
}
_area_volume_base_sorted = sorted(_area_volume_base.keys(), key=len, reverse=True)

_area_volume_re = re.compile(
    r'([0-9]+(?:[.,][0-9]+)?)\s*'
    r'(' + '|'.join(_area_volume_base_sorted) + r')'
    r'([²³]|2|3)\b',
    re.IGNORECASE,
)


# ============================================================
# Compound units: km/h, m/s, ft/s, mi/h, etc.
# ============================================================

_compound_numerator = {
    'km': 'kilometer', 'm': 'meter', 'mi': 'mile', 'ft': 'foot',
}
_compound_denominator = {
    'h': 'hour', 's': 'second', 'min': 'minute',
}
_compound_num_sorted = sorted(_compound_numerator.keys(), key=len, reverse=True)
_compound_den_sorted = sorted(_compound_denominator.keys(), key=len, reverse=True)

_compound_unit_re = re.compile(
    r'([0-9]+(?:[.,][0-9]+)?)\s*'
    r'(' + '|'.join(_compound_num_sorted) + r')'
    r'/\s*(' + '|'.join(_compound_den_sorted) + r')\b',
    re.IGNORECASE,
)


# ============================================================
# Temperature: 98.6°F, 37°C
# ============================================================

_temperature_re = re.compile(
    r'([0-9]+(?:\.[0-9]+)?)\s*°\s*([FfCc])\b'
)


# ============================================================
# Dimensions: 5x10, 3x4x5, 5x10in
# ============================================================

_dimension_re = re.compile(
    r'\b(\d+(?:[,.]?\d+)?\s*[xX]\s*\d+(?:[,.]?\d+)?'
    r'(?:\s*[xX]\s*\d+(?:[,.]?\d+)?)?'
    r'(?:\s*(?:in|inch|m|cm|mm|ft))?)\b'
)
_dimension_key = {
    'm': 'meter', 'in': 'inch', 'inch': 'inch',
    'cm': 'centimeter', 'mm': 'millimeter', 'ft': 'foot',
}


# ============================================================
# Mixed letter-number sequences: AK47, B2, MP3, etc.
# ============================================================

_letters_and_numbers_re = re.compile(
    r"((?:[a-zA-Z]+[0-9]|[0-9]+[a-zA-Z])[a-zA-Z0-9']*)", re.IGNORECASE)


# ============================================================
# Expansion functions
# ============================================================

def _expand_hardware(m):
    """Expand measurement unit abbreviations with correct pluralization.

    Examples:
        '5km' -> '5 kilometers'
        '1ft' -> '1 foot'
        '100mph' -> '100 miles per hour'
    """
    quantity = m.group(1)
    measure = m.group(2)
    unit = _hardware_key[measure.lower()]
    qty_num = float(quantity.replace(',', ''))

    # Don't pluralize compound phrases (contain spaces) or units ending in z/s
    if qty_num != 1 and ' ' not in unit:
        if unit in _irregular_plurals:
            unit = _irregular_plurals[unit]
        elif not unit.endswith(('z', 's')):
            unit += 's'

    return "{} {}".format(quantity, unit)


def _expand_area_volume(m):
    """Expand area (m2/m²) and volume (m3/m³) units.

    Examples:
        '100m2' -> '100 square meters'
        '50km²' -> '50 square kilometers'
        '10m3'  -> '10 cubic meters'
    """
    quantity = m.group(1)
    base = m.group(2)
    power = m.group(3)
    unit = _area_volume_base.get(base.lower(), base)
    qty_num = float(quantity.replace(',', ''))

    # Pluralize
    if qty_num != 1:
        if unit in _irregular_plurals:
            unit = _irregular_plurals[unit]
        elif not unit.endswith('s'):
            unit += 's'

    if power in ('²', '2'):
        return "{} square {}".format(quantity, unit)
    elif power in ('³', '3'):
        return "{} cubic {}".format(quantity, unit)
    return m.group(0)


def _expand_compound_unit(m):
    """Expand compound units like km/h, m/s.

    Examples:
        '100km/h'  -> '100 kilometers per hour'
        '5m/s'     -> '5 meters per second'
    """
    quantity = m.group(1)
    num_unit = _compound_numerator[m.group(2).lower()]
    den_unit = _compound_denominator[m.group(3).lower()]
    qty_num = float(quantity.replace(',', ''))

    # Pluralize numerator
    if qty_num != 1:
        if num_unit in _irregular_plurals:
            num_unit = _irregular_plurals[num_unit]
        elif not num_unit.endswith('s'):
            num_unit += 's'

    return "{} {} per {}".format(quantity, num_unit, den_unit)


def _expand_temperature(m):
    """Expand temperature with degree symbol.

    Examples:
        '98.6°F' -> '98.6 degrees fahrenheit'
        '37°C'   -> '37 degrees celsius'
    """
    quantity = m.group(1)
    scale = m.group(2).upper()
    scale_word = 'fahrenheit' if scale == 'F' else 'celsius'
    return "{} degrees {}".format(quantity, scale_word)


def _expand_dimension(m):
    """Expand dimension patterns like 5x10, 3x4x5.

    Examples:
        '5x10'    -> '5 by 10'
        '3x4x5in' -> '3 by 4 by 5 inch'
    """
    text = "".join([x for x in m.groups(0) if x != 0])
    text = text.replace(' x ', ' by ').replace('x', ' by ').replace('X', ' by ')
    for suffix, word in sorted(_dimension_key.items(), key=lambda x: len(x[0]), reverse=True):
        if text.endswith(suffix):
            text = text[:-len(suffix)].rstrip() + ' ' + word
            break
    return text


def _expand_letters_and_numbers(m):
    """Separate mixed letter-number sequences with spaces and group digits.

    Examples:
        'AK47'  -> 'AK 47'
        'B2'    -> 'B 2'
        'MP3'   -> 'MP 3'
        '1920s' -> '1920s'
    """
    text = re.split(r'(\d+)', m.group(0))

    # remove trailing space
    if text[-1] == '':
        text = text[:-1]
    elif text[0] == '':
        text = text[1:]

    # if not like 1920s, or AK47's , 20th, 1st, 2nd, 3rd, etc...
    if text[-1] in ("'s", "s", "th", "nd", "st", "rd") and text[-2].isdigit():
        text[-2] = text[-2] + text[-1]
        text = text[:-1]

    # for combining digits 2 by 2
    new_text = []
    for i in range(len(text)):
        string = text[i]
        if string.isdigit() and len(string) < 5:
            # heuristics
            if len(string) > 2 and string[-2] == '0':
                if string[-1] == '0':
                    string = [string]
                else:
                    string = [string[:-2], string[-2], string[-1]]
            elif len(string) % 2 == 0:
                string = [string[i:i+2] for i in range(0, len(string), 2)]
            elif len(string) > 2:
                string = [string[0]] + [string[i:i+2] for i in range(1, len(string), 2)]
            new_text.extend(string)
        else:
            new_text.append(string)

    text = new_text
    text = " ".join(text)
    return text


# ============================================================
# Main pipeline
# ============================================================

def normalize_letters_and_numbers(text):
    """Normalize measurement units, dimensions, temperatures, compound units,
    and mixed letter-number sequences.

    Processing order: most specific patterns first to avoid partial matches.
    """
    # New: compound units first (before hardware, since km/h contains km)
    text = re.sub(_compound_unit_re, _expand_compound_unit, text)
    # New: area/volume (before hardware, since m2 contains m)
    text = re.sub(_area_volume_re, _expand_area_volume, text)
    # New: temperature
    text = re.sub(_temperature_re, _expand_temperature, text)
    # Existing (expanded): measurement units
    text = re.sub(_hardware_re, _expand_hardware, text)
    # Existing: dimensions
    text = re.sub(_dimension_re, _expand_dimension, text)
    # Existing: mixed letter-number sequences
    text = re.sub(_letters_and_numbers_re, _expand_letters_and_numbers, text)
    return text
