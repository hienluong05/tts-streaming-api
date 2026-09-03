import re
import os
import sys

try:
    from .vietnamese_normalization.vi_cleaner import ViCleaner
    from .cleaners import english_cleaners_v2 as english_cleaners
except ImportError:
    from vietnamese_normalization.vi_cleaner import ViCleaner
    from cleaners import english_cleaners_v2 as english_cleaners

# Regex for detecting Vietnamese diacritics
_vi_diacritics_re = re.compile(
    r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]",
    re.IGNORECASE,
)


def detect_language(text):
    """
    Auto-detects language based on Vietnamese diacritics.
    Returns 'vi' if Vietnamese diacritics are found, otherwise 'en'.
    """
    if _vi_diacritics_re.search(text):
        return "vi"
    return "en"


def normalize(text, lang="auto"):
    """
    Normalizes the input text.
    :param text: The text to normalize.
    :param lang: 'vi' for Vietnamese, 'en' for English, or 'auto' to auto-detect.
    """
    if not text or not text.strip():
        return text

    if lang == "auto":
        lang = detect_language(text)

    if lang == "vi":
        cleaner = ViCleaner(text)
        return cleaner.clean()
    elif lang == "en":
        return english_cleaners(text)
    else:
        raise ValueError(f"Unsupported language: {lang}")


if __name__ == "__main__":
    # Test English
    en_text = "Authentication successful. VietinBank requires your confirmation for a transaction on card ending in 1234, occurring on 08/19/2026 at 10:00 AM, for the amount of $2,000.50 at Shopee."
    print("EN Input: ", en_text)
    print("EN Output:", normalize(en_text))
    print("-" * 50)

    # Test Vietnamese
    vi_text = "Dạ em đã xác thực thành công. VietinBank cần Anh/Chị xác nhận giao dịch thẻ có 4 số cuối 1234, phát sinh lúc 19/08/2026 10:00, số tiền 2,000,000 VND, tại Shopee."
    print("VI Input: ", vi_text)
    print("VI Output:", normalize(vi_text))
