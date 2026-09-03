from abc import ABC, abstractmethod
from typing import Generator, List, Optional
import numpy as np

class BaseTTSModel(ABC):
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Return list of supported language codes."""
        pass

    @abstractmethod
    def synthesize(self, text: str, language: Optional[str] = None, voice: Optional[str] = None) -> np.ndarray:
        """
        Synthesize speech and return complete audio array.
        Returns 1D numpy array.
        """
        pass

    @abstractmethod
    def synthesize_stream(self, text: str, language: Optional[str] = None, voice: Optional[str] = None) -> Generator[np.ndarray, None, None]:
        """
        Synthesize speech and yield audio chunks.
        Yields 1D numpy array chunks.
        """
        pass

    @abstractmethod
    def register_voice(self, voice_id: str, ref_audio_path: str) -> None:
        """
        Extract speaker embedding from reference audio and cache it.
        """
        pass

    @abstractmethod
    def get_sample_rate(self) -> int:
        """Return the sample rate of the generated audio."""
        pass
