"""English abbreviation, symbol, and URL normalization for TTS."""

import re

_no_period_re = re.compile(r'(No[.])(?=[ ]?[0-9])')
_percent_re = re.compile(r'([ ]?[%])')
_half_re = re.compile('([0-9]½)|(½)')
_url_re = re.compile(r'([a-zA-Z])\.(com|gov|org|net|edu|io|co|uk|us|ai|dev)')

# Hash/number sign: #1, #42
_hash_re = re.compile(r'#(\d+)')

# Plus between numbers: 2+2, 100 + 50
_plus_re = re.compile(r'(\d)\s*\+\s*(\d)')

# Equals sign between numbers: 2+2=4
_equals_re = re.compile(r'(\d)\s*=\s*(\d)')

# Slash between words (not URLs): input/output, and/or
_word_slash_re = re.compile(r'\b([a-zA-Z]+)/([a-zA-Z]+)\b')


# List of (regular expression, replacement) pairs for abbreviations:
_abbreviations = [(re.compile('\\b%s\\.' % x[0], re.IGNORECASE), x[1]) for x in [
    # Titles — personal
    ('mrs', 'misess'),
    ('ms', 'miss'),
    ('mr', 'mister'),
    ('dr', 'doctor'),
    ('prof', 'professor'),
    ('rev', 'reverend'),
    ('hon', 'honorable'),
    ('esq', 'esquire'),
    # Titles — military / government
    ('gen', 'general'),
    ('lt', 'lieutenant'),
    ('sgt', 'sergeant'),
    ('capt', 'captain'),
    ('col', 'colonel'),
    ('maj', 'major'),
    ('gov', 'governor'),
    ('sen', 'senator'),
    ('rep', 'representative'),
    ('pres', 'president'),
    ('supt', 'superintendent'),
    # Business
    ('co', 'company'),
    ('corp', 'corporation'),
    ('inc', 'incorporated'),
    ('ltd', 'limited'),
    ('assn', 'association'),
    ('bros', 'brothers'),
    ('dept', 'department'),
    ('mgr', 'manager'),
    ('admin', 'administrator'),
    # Titles — academic
    ('univ', 'university'),
    # Suffixes
    ('jr', 'junior'),
    ('sr', 'senior'),
    # Location
    ('st', 'saint'),
    ('ft', 'fort'),
    ('mt', 'mount'),
    ('ave', 'avenue'),
    ('blvd', 'boulevard'),
    ('apt', 'apartment'),
    ('hwy', 'highway'),
    # Common abbreviations
    ('etc', 'et cetera'),
    ('approx', 'approximately'),
    ('vs', 'versus'),
    ('vol', 'volume'),
    ('misc', 'miscellaneous'),
    ('est', 'established'),
]]


def _expand_no_period(m):
    word = m.group(0)
    if word[0] == 'N':
        return 'Number'
    return 'number'


def _expand_percent(m):
    return ' percent'


def _expand_half(m):
    word = m.group(1)
    if word is None:
        return 'half'
    return word[0] + ' and a half'


def _expand_urls(m):
    return f'{m.group(1)} dot {m.group(2)}'


def _expand_hash(m):
    return 'number ' + m.group(1)


def _expand_plus(m):
    return m.group(1) + ' plus ' + m.group(2)


def _expand_equals(m):
    return m.group(1) + ' equals ' + m.group(2)


def _expand_word_slash(m):
    return m.group(1) + ' or ' + m.group(2)


def normalize_abbreviations(text):
    """Normalize abbreviations, symbols, and special characters in English text.

    Processing order: specific patterns first, then general abbreviation list.
    """
    text = re.sub(_no_period_re, _expand_no_period, text)
    text = re.sub(_percent_re, _expand_percent, text)
    text = re.sub(_half_re, _expand_half, text)
    text = re.sub(_hash_re, _expand_hash, text)
    text = re.sub(_plus_re, _expand_plus, text)
    text = re.sub(_equals_re, _expand_equals, text)
    text = re.sub('&', ' and ', text)
    text = re.sub('@', ' at ', text)
    text = re.sub(_url_re, _expand_urls, text)
    text = re.sub(_word_slash_re, _expand_word_slash, text)

    for regex, replacement in _abbreviations:
        text = re.sub(regex, replacement, text)
    return text
