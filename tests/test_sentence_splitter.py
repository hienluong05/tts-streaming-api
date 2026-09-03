import pytest
from app.services.sentence_splitter import HierarchicalSentenceSplitter

def test_split_sentences():
    splitter = HierarchicalSentenceSplitter(min_chars=10, target_chars=50, max_chars=80)
    
    text = "Xin chào. Tôi tên là An. Hôm nay thời tiết rất đẹp."
    sentences = splitter.split_sentences(text)
    
    assert len(sentences) == 3
    assert sentences[0] == "Xin chào."
    assert sentences[1] == "Tôi tên là An."
    assert sentences[2] == "Hôm nay thời tiết rất đẹp."

def test_chunk_text():
    splitter = HierarchicalSentenceSplitter(min_chars=10, target_chars=50, max_chars=80)
    
    long_paragraph = (
        "Thưa quý vị khán giả, dự báo thời tiết ngày hôm nay tại khu vực thủ đô Hà Nội và các tỉnh đồng bằng Bắc Bộ "
        "tiếp tục duy trì trạng thái nhiều mây, có mưa rào và dông rải rác vài nơi."
    )
    chunks = splitter.chunk_text(long_paragraph)
    
    # Each chunk should be <= max_chars
    for chunk in chunks:
        assert len(chunk) <= splitter.max_chars
        
    # Total length should be roughly similar
    assert abs(len(" ".join(chunks)) - len(long_paragraph)) < 10
