import pytest
from app.services.text_normalizer import BilingualTextNormalizer

@pytest.fixture
def normalizer():
    return BilingualTextNormalizer()

def test_vietnamese_bank_keywords(normalizer):
    text = "Ngân hàng VCB và TCB, mã CVV là 123"
    result = normalizer.normalize(text, lang='vi')
    assert "Vietcombank" in result
    assert "Techcombank" in result
    assert "xi vi vi" in result.lower()

def test_english_bank_keywords(normalizer):
    text = "Bank VCB and TCB, CVC code is 456"
    result = normalizer.normalize(text, lang='en')
    assert "Vietcombank" in result
    assert "Techcombank" in result
    assert "C V C" in result

def test_vietnamese_money(normalizer):
    text = "Số dư là 15.500.000đ và 15,500,000 vnd."
    result = normalizer.normalize(text, lang='vi')
    assert "mười lăm triệu năm trăm nghìn" in result.lower()

def test_english_money(normalizer):
    text = "Balance is 15.500.000đ and $500."
    result = normalizer.normalize(text, lang='en')
    # Should contain fifteen million... and five hundred dollars
    assert "fifteen million five hundred thousand" in result.lower()
    assert "five hundred dollars" in result.lower()

def test_dates(normalizer):
    # Vietnamese
    vi_text = "Hạn thanh toán 15/09/2024"
    vi_res = normalizer.normalize(vi_text, lang='vi')
    assert "ngày 15 tháng 09 năm 2024" in vi_res or "ngày 15 tháng 9 năm 2024" in vi_res

    # English
    en_text = "Due date 15/09/2024"
    en_res = normalizer.normalize(en_text, lang='en')
    assert "15 09 2024" in en_res

def test_phone_numbers(normalizer):
    # Vietnamese
    vi_text = "Gọi 0987654321"
    vi_res = normalizer.normalize(vi_text, lang='vi')
    assert "0 9 8 7 6 5 4 3 2 1" in vi_res

    # English
    en_text = "Call 0987654321"
    en_res = normalizer.normalize(en_text, lang='en')
    assert "zero  9 8 7 6 5 4 3 2 1" in en_res or "zero" in en_res

def test_english_removes_vietnamese_accents(normalizer):
    text = "Mr. Nguyễn Văn A đã chuyển tiền."
    result = normalizer.normalize(text, lang='en')
    assert "Nguyen Van A" in result
    assert "Nguyễn" not in result
