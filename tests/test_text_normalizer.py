import pytest
from app.services.text_normalizer import VietnameseTextNormalizer

def test_text_normalizer_urls():
    normalizer = VietnameseTextNormalizer()
    text = "Vào trang web https://example.com nhé."
    result = normalizer.normalize(text)
    assert "https" not in result
    assert "example.com" not in result

def test_text_normalizer_vi_cleaner():
    normalizer = VietnameseTextNormalizer()
    text = "Hôm nay là ngày 25/12/2024, tôi đi từ TP. HCM."
    result = normalizer.normalize(text)
    # The ViCleaner converts everything to lowercase, expands dates and abbreviations
    assert "hai mươi lăm tháng mười hai" in result
    assert "thành phố hồ chí minh" in result
