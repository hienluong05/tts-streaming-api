import re
import logging
import sys
import os

# Add the project root to sys.path to ensure 'text' module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

logger = logging.getLogger(__name__)

class VietnameseTextNormalizer:
    def __init__(self, phoneticize_loanwords: bool = False):
        self.phoneticize_loanwords = phoneticize_loanwords
        self.cleaner = None
        try:
            from text.vietnamese_normalization.vi_cleaner import ViCleaner
            self.cleaner = ViCleaner()
            logger.info("Successfully loaded FastPitch ViCleaner for text normalization.")
        except ImportError as e:
            logger.warning(f"Could not import ViCleaner from text module: {e}")

    def normalize(self, text: str) -> str:
        if not text:
            return text

        # 1. Clean URLs and Emails before passing to cleaner, as ViCleaner might spell them out
        text = re.sub(r"https?://\S+|www\.\S+", "", text)
        text = re.sub(r"\S+@\S+", "", text)
        
        # 2. Clean repeating punctuation
        text = re.sub(r"\.{2,}", ".", text)
        text = re.sub(r"!{2,}", "!", text)
        text = re.sub(r"\?{2,}", "?", text)
        
        # 3. Apply the comprehensive ViCleaner pipeline
        if self.cleaner:
            try:
                text = self.cleaner.clean_text(text)
            except Exception as e:
                logger.error(f"Error during ViCleaner text normalization: {e}")
        else:
            # Fallback if cleaner failed to load
            text = text.lower()
            text = re.sub(r"\s+", " ", text).strip()
            
        return text.strip()
