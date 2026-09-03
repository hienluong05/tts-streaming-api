import os
import re
import urllib.request
from typing import Tuple
import fasttext

# Suppress FastText annoying C++ deprecation print warnings
fasttext.FastText.eprint = lambda x: None

class FastTextLanguageDetector:
    MODEL_URLS = {
        "bin": "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin",
        "ftz": "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz"
    }

    def __init__(self, model_type: str = "bin", model_dir: str = "models_cache"):
        self.model_type = model_type
        self.model_path = os.path.join(model_dir, f"lid.176.{model_type}")
        self._ensure_model(model_dir)
        self.model = fasttext.load_model(self.model_path)

    def _ensure_model(self, model_dir: str):
        if not os.path.exists(self.model_path):
            os.makedirs(model_dir, exist_ok=True)
            print(f"Downloading FastText {self.model_type} model...")
            urllib.request.urlretrieve(self.MODEL_URLS[self.model_type], self.model_path)
            print("Download complete.")

    def detect(self, text: str, min_confidence: float = 0.5, default_lang: str = "vi") -> Tuple[str, float]:
        """
        Detects language of input text.
        Returns: (lang_code, confidence_score)
        """
        clean_text = text.replace("\n", " ").strip()
        clean_text = re.sub(r"https?://\S+|www\.\S+", "", clean_text)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        if not clean_text or len(clean_text) < 2:
            return default_lang, 0.0

        labels, scores = self.model.predict(clean_text, k=1)
        lang = labels[0].replace("__label__", "")
        confidence = float(scores[0])

        if confidence < min_confidence:
            # Fallback: check if text has Vietnamese-specific diacritic characters
            has_vi_diacritics = bool(re.search(r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", clean_text, re.IGNORECASE))
            if has_vi_diacritics:
                return "vi", max(confidence, 0.75)
            return default_lang, confidence

        return lang, confidence
