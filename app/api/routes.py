import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response, StreamingResponse
from app.api.schemas import TTSRequest, DetectLanguageRequest, DetectLanguageResponse, VoiceResponse
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
    # 1. Detect language if not provided
    lang = request.language
    if not lang:
        lang, _ = language_detector.detect(request.text)
        
    # 2. Normalize text (only if Vietnamese)
    if lang == "vi":
        text = text_normalizer.normalize(request.text)
    else:
        text = request.text
        
    # 3. Synthesize
    try:
        audio, sample_rate = model_manager.synthesize(text, lang, request.voice)
        wav_bytes = numpy_to_wav_bytes(audio, sample_rate)
        return Response(content=wav_bytes, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts/stream")
async def synthesize_speech_stream(request: TTSRequest):
    # 1. Detect language
    lang = request.language
    if not lang:
        lang, _ = language_detector.detect(request.text)
        
    # 2. Normalize text
    if lang == "vi":
        text = text_normalizer.normalize(request.text)
    else:
        text = request.text
        
    # 3. Split into chunks for streaming
    chunks = sentence_splitter.chunk_text(text)
    
    if not chunks:
        raise HTTPException(status_code=400, detail="No valid text to synthesize")
        
    def audio_generator():
        try:
            # We don't know sample rate until we pick the model
            # Just grab it from the model manager's selected model
            model = model_manager._select_model(lang)
            sample_rate = model.get_sample_rate()
            
            # Send WAV header first for browser compatibility
            yield create_wav_header(sample_rate)
            
            for chunk in chunks:
                audio_stream, _ = model_manager.synthesize_stream(chunk, lang, request.voice)
                for audio_chunk in audio_stream:
                    yield numpy_to_pcm16_bytes(audio_chunk)
        except Exception as e:
            print(f"Streaming error: {e}")
            
    return StreamingResponse(audio_generator(), media_type="audio/wav")
