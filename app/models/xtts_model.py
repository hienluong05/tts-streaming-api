import logging
from typing import Generator, List, Optional
import numpy as np
from app.models.base import BaseTTSModel

logger = logging.getLogger(__name__)

class XTTSModel(BaseTTSModel):
    def __init__(self, config_path: str = None, checkpoint_dir: str = None):
        logger.info("Initializing XTTSModel...")
        try:
            import torch
            from TTS.tts.configs.xtts_config import XttsConfig
            from TTS.tts.models.xtts import Xtts
            
            if config_path and checkpoint_dir:
                config = XttsConfig()
                config.load_json(config_path)
                self.model = Xtts.init_from_config(config)
                self.model.load_checkpoint(config, checkpoint_dir=checkpoint_dir, eval=True)
                if torch.cuda.is_available():
                    self.model.cuda()
                else:
                    logger.warning("CUDA not available, running XTTS on CPU is very slow.")
            else:
                logger.warning("XTTS config or checkpoint not provided. Dummy init.")
                self.model = None
                
        except ImportError:
            logger.warning("TTS package not found. XTTSModel will not function.")
            self.model = None
            
        self._speaker_cache = {}

    def get_supported_languages(self) -> List[str]:
        # 17 languages supported by XTTS v2
        return ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "hu", "ko", "ja", "hi", "vi"]

    def register_voice(self, voice_id: str, ref_audio_path: str) -> None:
        if not self.model:
            raise RuntimeError("XTTS is not initialized.")
        logger.info(f"Encoding reference for voice {voice_id} using XTTS...")
        gpt_latent, spk_embed = self.model.get_conditioning_latents(audio_path=[ref_audio_path])
        self._speaker_cache[voice_id] = (gpt_latent, spk_embed)
        logger.info(f"Voice {voice_id} cached successfully.")

    def synthesize(self, text: str, language: Optional[str] = "en", voice: Optional[str] = None) -> np.ndarray:
        if not self.model:
            raise RuntimeError("XTTS is not initialized.")
        
        # Default to a generic voice if not found
        if voice and voice in self._speaker_cache:
            gpt_latent, spk_embed = self._speaker_cache[voice]
        else:
            raise ValueError(f"Voice {voice} not registered in XTTS cache.")

        out = self.model.inference(
            text=text,
            language=language,
            gpt_cond_latent=gpt_latent,
            speaker_embedding=spk_embed,
            temperature=0.7,
            repetition_penalty=2.0
        )
        return np.array(out["wav"])

    def synthesize_stream(self, text: str, language: Optional[str] = "en", voice: Optional[str] = None) -> Generator[np.ndarray, None, None]:
        if not self.model:
            raise RuntimeError("XTTS is not initialized.")
            
        if voice and voice in self._speaker_cache:
            gpt_latent, spk_embed = self._speaker_cache[voice]
        else:
            raise ValueError(f"Voice {voice} not registered in XTTS cache.")

        chunks = self.model.inference_stream(
            text=text,
            language=language,
            gpt_cond_latent=gpt_latent,
            speaker_embedding=spk_embed,
            stream_chunk_size=20
        )
        
        for chunk in chunks:
            yield chunk.cpu().numpy()

    def get_sample_rate(self) -> int:
        return 24000
