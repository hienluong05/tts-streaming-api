import logging
from typing import Generator, List, Optional
import numpy as np
from app.models.base import BaseTTSModel

logger = logging.getLogger(__name__)

class VieNeuTTSModel(BaseTTSModel):
    def __init__(self):
        logger.info("Initializing VieNeuTTSModel (v3turbo, onnx backend)...")
        try:
            from vieneu import Vieneu
            # CPU/ONNX for streaming low-latency as recommended
            self.tts = Vieneu(mode="v3turbo", backend="onnx")
        except ImportError:
            logger.warning("vieneu package not found. Model will not function.")
            self.tts = None
            
        self._voice_cache = {}  # {voice_id: speaker_embedding}

    def get_supported_languages(self) -> List[str]:
        return ["vi", "en"]

    def register_voice(self, voice_id: str, ref_audio_path: str) -> None:
        if not self.tts:
            raise RuntimeError("VieNeu is not installed.")
        logger.info(f"Encoding reference for voice {voice_id} using VieNeu...")
        embedding = self.tts.encode_reference(ref_audio_path)
        self._voice_cache[voice_id] = embedding
        logger.info(f"Voice {voice_id} cached successfully.")

    def _get_voice_param(self, voice: Optional[str]):
        # If voice is in cache, return the embedding, else assume it's a preset string or None
        if voice and voice in self._voice_cache:
            return self._voice_cache[voice]
        return voice

    def synthesize(self, text: str, language: Optional[str] = None, voice: Optional[str] = None) -> np.ndarray:
        if not self.tts:
            raise RuntimeError("VieNeu is not installed.")
        voice_param = self._get_voice_param(voice)
        # VieNeu handles Vi-En code switching automatically, 'language' param is not strictly needed for v3turbo
        return self.tts.infer(text=text, voice=voice_param)

    def synthesize_stream(self, text: str, language: Optional[str] = None, voice: Optional[str] = None) -> Generator[np.ndarray, None, None]:
        if not self.tts:
            raise RuntimeError("VieNeu is not installed.")
        voice_param = self._get_voice_param(voice)
        for chunk in self.tts.infer_stream(text=text, voice=voice_param):
            yield chunk

    def get_sample_rate(self) -> int:
        return 48000
