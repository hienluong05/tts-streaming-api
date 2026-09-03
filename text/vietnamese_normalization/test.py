from .vi_cleaner import ViCleaner

cleaner = ViCleaner()
text = "Tỉ số 2 - 1"
cleaned_text = cleaner.clean_text(text)
print(cleaned_text)  # Output: "Từ 5-10 triệu đồng, còn 1.000.000 đồng nữa là đủ."
