from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Vietnamese TTS Streaming API"
    version: str = "1.0.0"
    
    # Storage paths
    reference_voices_dir: str = "reference_voices"
    speaker_embeddings_dir: str = "speaker_embeddings"
    models_cache_dir: str = "models_cache"
    
    # Model settings
    use_xtts_fallback: bool = False  # Enable when XTTS is configured

    class Config:
        env_file = ".env"

settings = Settings()
