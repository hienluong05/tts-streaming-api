# ============================================================
# Stage 1: Builder — install dependencies in a clean layer
# ============================================================
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r /tmp/requirements.txt

# ============================================================
# Stage 2: Runtime — lean production image
# ============================================================
FROM python:3.11-slim AS runtime

# System dependency: espeak-ng is required by VieNeu phonemizer (sea-g2p)
RUN apt-get update && apt-get install -y --no-install-recommends \
    espeak-ng \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Create non-root user (Commented out to avoid volume permission issues on host OS)
# RUN useradd --create-home appuser
# USER appuser
WORKDIR /app

# Copy application code
COPY . .

# Create persistent directories
RUN mkdir -p reference_voices speaker_embeddings models_cache

# Pre-download TTS model weights during build (bakes into image, ~400MB)
# Uncomment the line below to avoid downloading on first request:
# RUN python -c "from vieneu import Vieneu; Vieneu(mode='v3turbo', backend='onnx')"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
