import re

_percent_re = re.compile(r"([ ]?[%])")
_url_re = re.compile(r"([a-zA-Z])\.(com|gov|org|vn|com\.vn|edu\.vn)")


_abbreviations_vi = {
    r"v\.v": " vân vân. ",
    "v/v": "về việc",
    "đ/c": "địa chỉ",
    "k/g": "kính gửi",
    "th/g": "thân gửi",
    "ko": "không",
    "k": "không",
    "bit": "biết",
    "bik": "biết",
    "l/h": "liên hệ",
    "gd": "giao dịch",
    "anh/chị": "anh chị",
    "otp": "ô tê pê",
    "đc": "được",
    "dc": "được",
    "vs": "với",
    "tks": "cảm ơn",
    "thks": "cảm ơn",
    "hqua": "hôm qua",
    "hnay": "hôm nay",
    "hmai": "ngày mai",
    "z": "vậy",
}

_abbreviations_combine_re = r"(" + "|".join(_abbreviations_vi.keys()) + r")"

def _expand_percent_vi(m):
    return " phần trăm"


def _expand_urls_vi(m):
    return f"{m.group(1)} chấm {m.group(2).replace('.', ' chấm ')}"


def _expand_abbreviations_vi(m):
    key = m.group(0)
    key = key.replace(".", r"\.").lower()
    return _abbreviations_vi.get(key, m.group(0))


def normalize_abbreviations_vi(text):
    text = normalize_speacial_symbol_vi(text)
    text = re.sub(_url_re, _expand_urls_vi, text)
    text = re.sub(r"(?i)(?<!\w)" + _abbreviations_combine_re + r"(?!\w)", _expand_abbreviations_vi, text)
    return text


def normalize_speacial_symbol_vi(text):
    text = re.sub(_percent_re, _expand_percent_vi, text)
    text = re.sub("&", " và ", text)
    text = re.sub("@", " a còng ", text)
    text = re.sub(r"\+", " cộng ", text)
    text = re.sub("//", " xuyệt ", text)
    return text
