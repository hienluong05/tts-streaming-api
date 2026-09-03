
from app.services.sentence_splitter import HierarchicalSentenceSplitter
splitter = HierarchicalSentenceSplitter(min_chars=10, target_chars=50, max_chars=80)
text = 'Xin chào. Tôi tên là An. Hôm nay th?i ti?t r?t d?p.'
sentences = splitter.split_sentences(text)
print('sentences:', sentences)

