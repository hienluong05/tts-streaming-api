from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class OutputFormat(str, Enum):
    WAV = "wav"
    PCM = "pcm"
    BASE64 = "b64"

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize")
    language: Optional[str] = Field(None, description="Language code (e.g. 'vi', 'en'). Auto-detected if None.")
    voice: Optional[str] = Field(None, description="Preset voice name or custom voice ID")
    speed: float = Field(1.0, description="Speech speed multiplier")
    stream: bool = Field(False, description="Whether to stream response")
    output_format: OutputFormat = Field(OutputFormat.WAV, description="Output format: 'wav' (binary file), 'pcm' (raw PCM bytes), 'b64' (base64 JSON)")

class TTSResponse(BaseModel):
    audio_b64: str = Field(..., description="Base64-encoded WAV audio")
    sample_rate: int = Field(..., description="Audio sample rate in Hz")
    format: str = Field("wav", description="Audio format inside the base64 payload")
    language_detected: Optional[str] = Field(None, description="Auto-detected language code")
    model_used: str = Field(..., description="The name of the AI model that generated this audio")

class DetectLanguageRequest(BaseModel):
    text: str = Field(..., description="Text to detect language for")

class DetectLanguageResponse(BaseModel):
    language: str = Field(..., description="Detected language code")
    confidence: float = Field(..., description="Confidence score")

class VoiceResponse(BaseModel):
    voice_id: str = Field(..., description="Registered voice ID")
    status: str = Field(..., description="Registration status")
