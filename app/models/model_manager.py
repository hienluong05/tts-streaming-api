import logging
from typing import Optional, Generator
import numpy as np

from app.config import settings
from app.models.base import BaseTTSModel
from app.models.vieneu_model import VieNeuTTSModel
from app.models.xtts_model import XTTSModel

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self):
        self.primary_model: BaseTTSModel = None
        self.fallback_model: BaseTTSModel = None

    def initialize_models(self):
        logger.info("Initializing TTS models...")
        # Initialize primary model (VieNeu)
        self.primary_model = VieNeuTTSModel()
        
        # Initialize fallback model (XTTS) if configured
        if settings.use_xtts_fallback:
            import os
            xtts_dir = "/models/viXTTS"
            if not os.path.exists(xtts_dir):
                xtts_dir = os.path.join(os.getcwd(), settings.models_cache_dir, "viXTTS")
            
            config_path = os.path.join(xtts_dir, "config.json")
            if os.path.exists(config_path):
                self.fallback_model = XTTSModel(config_path=config_path, checkpoint_dir=xtts_dir)
            else:
                logger.warning(f"XTTS cache not found at {xtts_dir}. Initializing dummy XTTSModel.")
                self.fallback_model = XTTSModel()
        else:
            logger.info("XTTS fallback is disabled in settings.")

    def _select_model(self, language: str) -> BaseTTSModel:
        if not language or language.lower() in ['vi', 'en']:
            return self.primary_model
        
        if self.fallback_model and language.lower() in self.fallback_model.get_supported_languages():
            return self.fallback_model
            
        # Default to primary if language not supported by fallback, or fallback disabled
        return self.primary_model

    def register_voice(self, voice_id: str, ref_audio_path: str, model_type: str = "auto") -> None:
        """Register a voice with the specified model, or both."""
        if model_type in ["auto", "vieneu"]:
            if self.primary_model:
                self.primary_model.register_voice(voice_id, ref_audio_path)
        
        if model_type in ["auto", "xtts"] and self.fallback_model:
            self.fallback_model.register_voice(voice_id, ref_audio_path)

    def synthesize(self, text: str, language: Optional[str] = None, voice: Optional[str] = None) -> tuple[np.ndarray, int]:
        """Synthesize and return audio + sample rate"""
        model = self._select_model(language)
        audio = model.synthesize(text, language, voice)
        return audio, model.get_sample_rate()

    def synthesize_stream(self, text: str, language: Optional[str] = None, voice: Optional[str] = None) -> tuple[Generator[np.ndarray, None, None], int]:
        """Stream synthesize and return chunk generator + sample rate"""
        model = self._select_model(language)
        chunks = model.synthesize_stream(text, language, voice)
        return chunks, model.get_sample_rate()

# Singleton instance
model_manager = ModelManager()
