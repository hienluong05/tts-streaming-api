import os
import base64
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response, StreamingResponse
from app.api.schemas import (
    TTSRequest, TTSResponse, OutputFormat,
    DetectLanguageRequest, DetectLanguageResponse, VoiceResponse,
)
from app.models.model_manager import model_manager
from app.services.language_detector import FastTextLanguageDetector
from app.services.text_normalizer import VietnameseTextNormalizer
from app.services.sentence_splitter import HierarchicalSentenceSplitter
from app.utils.audio import numpy_to_wav_bytes, create_wav_header, numpy_to_pcm16_bytes
from app.config import settings

router = APIRouter()

# Initialize services
language_detector = FastTextLanguageDetector()
text_normalizer = VietnameseTextNormalizer(phoneticize_loanwords=False)
sentence_splitter = HierarchicalSentenceSplitter(min_chars=40, target_chars=120, max_chars=160)

# Initialize models
model_manager.initialize_models()


def _preprocess(text: str, language: str = None):
    """Detect language + normalize text. Returns (processed_text, detected_lang)."""
    lang = language
    if not lang:
        lang, _ = language_detector.detect(text)
    if lang == "vi":
        text = text_normalizer.normalize(text)
    return text, lang


@router.post("/detect-language", response_model=DetectLanguageResponse)
async def detect_language(request: DetectLanguageRequest):
    lang, conf = language_detector.detect(request.text)
    return DetectLanguageResponse(language=lang, confidence=conf)


@router.post("/voices")
async def upload_voice(voice_id: str = Form(...), file: UploadFile = File(...)):
    """Upload a reference audio file to create a voice profile."""
    if not file.filename.endswith((".wav", ".mp3", ".flac")):
        raise HTTPException(status_code=400, detail="Only WAV, MP3, or FLAC files are supported")

    file_path = os.path.join(settings.reference_voices_dir, f"{voice_id}_{file.filename}")

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        model_manager.register_voice(voice_id, file_path)
        return VoiceResponse(voice_id=voice_id, status="Registered successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register voice: {str(e)}")


@router.post("/tts")
async def synthesize_speech(request: TTSRequest):
    text, lang = _preprocess(request.text, request.language)
    model = model_manager._select_model(lang)
    model_name = model.__class__.__name__

    try:
        audio = model.synthesize(text, lang, request.voice)
        sample_rate = model.get_sample_rate()
        wav_bytes = numpy_to_wav_bytes(audio, sample_rate)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # ── Return theo output_format ──
    if request.output_format == OutputFormat.BASE64:
        audio_b64 = base64.b64encode(wav_bytes).decode("utf-8")
        return TTSResponse(
            audio_b64=audio_b64,
            sample_rate=sample_rate,
            format="wav",
            language_detected=lang,
            model_used=model_name
        )

    if request.output_format == OutputFormat.PCM:
        from app.utils.audio import numpy_to_pcm16_bytes
        pcm_bytes = numpy_to_pcm16_bytes(audio)
        return Response(content=pcm_bytes, media_type="audio/pcm", headers={"X-Model-Used": model_name})

    # Default: WAV binary
    return Response(content=wav_bytes, media_type="audio/wav", headers={"X-Model-Used": model_name})


@router.post("/tts/stream")
async def synthesize_speech_stream(request: TTSRequest):
    text, lang = _preprocess(request.text, request.language)

    chunks = sentence_splitter.chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No valid text to synthesize")

    model = model_manager._select_model(lang)
    model_name = model.__class__.__name__

    def audio_generator():
        try:
            sample_rate = model.get_sample_rate()
            
            # Send WAV header first for browser compatibility
            yield create_wav_header(sample_rate)
            
            for chunk in chunks:
                audio_stream = model.synthesize_stream(chunk, lang, request.voice)
                for audio_chunk in audio_stream:
                    yield numpy_to_pcm16_bytes(audio_chunk)
        except Exception as e:
            print(f"Streaming error: {e}")

    return StreamingResponse(
        audio_generator(), 
        media_type="audio/wav",
        headers={"X-Model-Used": model_name}
    )
