import re

from .symbol_vi import vietnamese_without_num_re

_currency_key = {
    r"\$": "đô la",
    "£": "bảng",
    "€": "ơ rô",
    "₩": "uân",
    "₫": "đồng",
    "usd": "đô la",
    "euro": "ơ rô",
    "eur": "ơ rô",
    "vnd": "đồng",
    "vnđ": "đồng",
    "đ": "đồng",
    "¥": "yên",
    "ndt": "nhân dân tệ",
    "k": "nghìn",
}

_currency_combine_regex = r"(" + "|".join(_currency_key.keys()) + r")"

# Match currency symbol BEFORE number (e.g. $1.5, $ 100, $1.5M, $100k)
_currency_before_num_re = re.compile(
    r"(?i)(?<!\w)"
    + _currency_combine_regex
    + r"\s*(\d+(?:[.,]\d+)?)\s*([mMkKmMbB]?)\b"
)

# Match currency symbol AFTER number (e.g. 1.5$, 100 USD, 1.5M $, 100k VNĐ)
_currency_after_num_re = re.compile(
    r"(?i)\b(\d+(?:[.,]\d+)?)\s*([mMkKmMbB]?)\s*"
    + _currency_combine_regex
    + r"(?!\w)"
)

# Match isolated currency symbols (fallback)
_isolated_currency_re = re.compile(
    r"(?i)(?<!\w)" + _currency_combine_regex + r"(?!\w)"
)

_magnitude_key = {
    "m": "triệu",
    "b": "tỷ",
    "k": "nghìn",
}

def _expand_currency_value(value, magnitude, currency):
    # e.g. 1.5, m, $ -> 1.5 triệu đô la
    # Wait, the number expanding will happen in numerical_vi.py later.
    # We just need to replace the currency and magnitude with words,
    # and put them AFTER the number.
    # So "$1.5M" -> "1.5 triệu đô la"
    
    currency_word = _currency_key.get(currency.lower(), currency)
    
    if currency.lower() == "$":
        currency_word = _currency_key[r"\$"]
        
    mag_word = ""
    if magnitude:
        mag_word = " " + _magnitude_key.get(magnitude.lower(), magnitude.lower())
        
    return f"{value}{mag_word} {currency_word}"


def _expand_currency_before(match):
    currency = match.group(1)
    value = match.group(2)
    magnitude = match.group(3)
    return _expand_currency_value(value, magnitude, currency)


def _expand_currency_after(match):
    value = match.group(1)
    magnitude = match.group(2)
    currency = match.group(3)
    return _expand_currency_value(value, magnitude, currency)


def _expand_isolated_currency(match):
    currency = match.group(1)
    if currency.lower() == "$":
        return _currency_key[r"\$"]
    return _currency_key.get(currency.lower(), currency)


def normalize_currency_vi(text):
    text = re.sub(_currency_before_num_re, _expand_currency_before, text)
    text = re.sub(_currency_after_num_re, _expand_currency_after, text)
    text = re.sub(_isolated_currency_re, _expand_isolated_currency, text)
    return text
