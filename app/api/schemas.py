from pydantic import BaseModel, Field
from typing import Optional

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize")
    language: Optional[str] = Field(None, description="Language code (e.g. 'vi', 'en'). Auto-detected if None.")
    voice: Optional[str] = Field(None, description="Preset voice name or custom voice ID")
    speed: float = Field(1.0, description="Speech speed multiplier")
    stream: bool = Field(False, description="Whether to stream response")
    output_format: str = Field("wav", description="Output audio format (wav, mp3, pcm)")

class DetectLanguageRequest(BaseModel):
    text: str = Field(..., description="Text to detect language for")

class DetectLanguageResponse(BaseModel):
    language: str = Field(..., description="Detected language code")
    confidence: float = Field(..., description="Confidence score")

class VoiceResponse(BaseModel):
    voice_id: str = Field(..., description="Registered voice ID")
    status: str = Field(..., description="Registration status")
