# Vietnamese TTS Streaming API

This is a production-grade FastAPI service for Text-to-Speech with Voice Cloning, optimized for Vietnamese language. It supports native audio streaming via WebSocket/HTTP chunking and zero-shot voice cloning.

## Features
- **Dual-Model Architecture**: Uses `VieNeu-TTS v3 Turbo` for ultra-low latency Vietnamese/English code-switching and `XTTS v2` for multilingual support (17 languages).
- **FastText Language Detection**: Automatically routes requests to the optimal model.
- **Vietnamese Text Normalization**: Handles numbers, dates, currencies, and common abbreviations via `vinorm` and custom rules.
- **Hierarchical Sentence Splitting**: Intelligently chunks text for natural prosody and low latency streaming (<300ms TTFB).
- **Real-time Streaming**: Yields raw PCM audio chunks frame-by-frame for seamless conversational AI integration.

## Installation

### Prerequisites
- Python 3.10 or 3.11
- `espeak-ng` installed on your system (`sudo apt-get install espeak-ng` on Ubuntu, `brew install espeak` on macOS)

### Setup
```bash
pip install -r requirements.txt
```

### Run Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Or via Docker:
```bash
docker-compose up --build
```

## API Usage

### 1. Register a Custom Voice
```bash
curl -X POST "http://localhost:8000/api/v1/voices" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "voice_id=my_custom_voice" \
  -F "file=@/path/to/reference_audio.wav"
```

### 2. Synthesize Speech
```bash
curl -X POST "http://localhost:8000/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Xin chào, hôm nay thời tiết rất đẹp.",
    "voice": "my_custom_voice"
  }' \
  --output output.wav
```

### 3. Stream Audio
```bash
curl -X POST "http://localhost:8000/api/v1/tts/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Xin chào, đây là luồng âm thanh theo thời gian thực.",
    "voice": "my_custom_voice"
  }' \
  --output stream.wav
```
