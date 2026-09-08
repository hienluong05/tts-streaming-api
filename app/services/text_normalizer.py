import re
import logging
import sys
import os

# Add the project root to sys.path to ensure 'text' module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

logger = logging.getLogger(__name__)

# Try to load num2words
try:
    from num2words import num2words
    HAS_NUM2WORDS = True
except ImportError:
    HAS_NUM2WORDS = False
    logger.warning("num2words not found. English money reading will be limited.")

# Try to load vietnam-number
try:
    from vietnam_number import n2w
    HAS_VIETNAM_NUMBER = True
except ImportError:
    HAS_VIETNAM_NUMBER = False
    logger.warning("vietnam-number not found. Vietnamese money reading will be limited.")


class BilingualTextNormalizer:
    def __init__(self, phoneticize_loanwords: bool = False):
        self.phoneticize_loanwords = phoneticize_loanwords
        self.vi_cleaner = None
        try:
            from text.vietnamese_normalization.vi_cleaner import ViCleaner
            self.vi_cleaner = ViCleaner()
            logger.info("Successfully loaded FastPitch ViCleaner for text normalization.")
        except ImportError as e:
            logger.warning(f"Could not import ViCleaner from text module: {e}")

        self.bank_map = {
            "vcb": "Vietcombank", "vietcombank": "Vietcombank",
            "tcb": "Techcombank", "techcombank": "Techcombank",
            "bidv": "B I D V",
            "vpb": "VPBank", "vpbank": "VPBank",
            "mbb": "MB Bank", "mbbank": "MB Bank",
            "vtb": "VietinBank", "vietinbank": "VietinBank",
            "agr": "Agribank", "agribank": "Agribank",
            "acb": "A C B",
            "shb": "S H B",
            "vib": "V I B",
        }

    def _remove_accents(self, text: str) -> str:
        s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
        s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'
        s = ''
        for c in text:
            if c in s1:
                s += s0[s1.index(c)]
            else:
                s += c
        return s

    def _normalize_common(self, text: str, lang: str) -> str:
        text = re.sub(r"https?://\S+|www\.\S+", "", text)
        text = re.sub(r"\S+@\S+", "", text)
        
        # CVV / CVC
        if lang == 'vi':
            text = re.sub(r'\b(cvv|CVV)\b', 'xi vi vi', text, flags=re.IGNORECASE)
            text = re.sub(r'\b(cvc|CVC)\b', 'xi vi xi', text, flags=re.IGNORECASE)
        else:
            text = re.sub(r'\b(cvv|CVV)\b', 'C V V', text, flags=re.IGNORECASE)
            text = re.sub(r'\b(cvc|CVC)\b', 'C V C', text, flags=re.IGNORECASE)
            
        # Banks
        def bank_repl(m):
            b = m.group(1).lower()
            return self.bank_map.get(b, m.group(1))
        
        pattern = re.compile(r'\b(' + '|'.join(self.bank_map.keys()) + r')\b', re.IGNORECASE)
        text = pattern.sub(bank_repl, text)
        return text

    def _normalize_vi(self, text: str) -> str:
        # Phone numbers: 09... (read digit by digit)
        def phone_repl(m):
            return " ".join(list(m.group(1)))
        text = re.sub(r'\b(0\d{9,10})\b', phone_repl, text)

        # Dates DD/MM/YYYY
        text = re.sub(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', r'ngày \1 tháng \2 năm \3', text)
        
        # Money (d, vnđ, $)
        if HAS_VIETNAM_NUMBER:
            def money_repl_vnd(m):
                num_str = m.group(1).replace('.', '').replace(',', '')
                try:
                    words = n2w(num_str)
                    return words + " đồng"
                except:
                    return m.group(0)
            text = re.sub(r'\b(\d{1,3}(?:[.,]\d{3})*|\d+)\s*(?:vnđ|vnd|đ|d)\b', money_repl_vnd, text, flags=re.IGNORECASE)
            
            def money_repl_usd(m):
                num_str = m.group(1).replace('.', '').replace(',', '')
                try:
                    words = n2w(num_str)
                    return words + " đô la"
                except:
                    return m.group(0)
            text = re.sub(r'\$\s*(\d{1,3}(?:[.,]\d{3})*|\d+)\b', money_repl_usd, text)

        # Repeating punctuation
        text = re.sub(r"\.{2,}", ".", text)
        text = re.sub(r"!{2,}", "!", text)
        text = re.sub(r"\?{2,}", "?", text)
        
        # Apply vi_cleaner
        if self.vi_cleaner:
            try:
                text = self.vi_cleaner.clean_text(text)
            except Exception as e:
                logger.error(f"Error during ViCleaner: {e}")
        else:
            text = text.lower()
            text = re.sub(r"\s+", " ", text).strip()
            
        return text.strip()

    def _normalize_en(self, text: str) -> str:
        # Phone numbers
        def phone_repl(m):
            return " ".join(list(m.group(1))).replace('0', 'zero ')
        text = re.sub(r'\b(0\d{9,10})\b', phone_repl, text)

        # Dates
        text = re.sub(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', r'\1 \2 \3', text)
        
        # Money
        if HAS_NUM2WORDS:
            def money_repl_vnd(m):
                num_str = m.group(1).replace(',', '').replace('.', '')
                try:
                    words = num2words(int(num_str), lang='en')
                    return words + " dong"
                except:
                    return m.group(0)
            text = re.sub(r'\b(\d{1,3}(?:[.,]\d{3})*|\d+)\s*(?:vnđ|vnd|đ|d)\b', money_repl_vnd, text, flags=re.IGNORECASE)
            
            def money_repl_usd(m):
                num_str = m.group(1).replace(',', '').replace('.', '')
                try:
                    words = num2words(int(num_str), lang='en')
                    return words + " dollars"
                except:
                    return m.group(0)
            text = re.sub(r'\$\s*(\d{1,3}(?:[.,]\d{3})*|\d+)\b', money_repl_usd, text)

        # Remove Vietnamese accents for English XTTS
        text = self._remove_accents(text)

        # Punctuation
        text = re.sub(r"\.{2,}", ".", text)
        text = re.sub(r"!{2,}", "!", text)
        text = re.sub(r"\?{2,}", "?", text)
        return text.strip()

    def normalize(self, text: str, lang: str = 'vi') -> str:
        if not text:
            return text
            
        lang = lang.lower() if lang else 'vi'
        
        text = self._normalize_common(text, lang)
        
        if lang == 'vi':
            return self._normalize_vi(text)
        elif lang == 'en':
            return self._normalize_en(text)
        else:
            return text
