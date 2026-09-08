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

# ── Pre-download model weights during build (baked into image) ──
# 1. VieNeu TTS model (~400MB) — avoids HuggingFace download at runtime
RUN python -c "from vieneu import Vieneu; Vieneu(mode='v3turbo', backend='onnx')"

# 2. XTTS model — downloaded to an external path to avoid being masked by volume mounts
RUN pip install huggingface_hub && \
    python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='capleaf/viXTTS', local_dir='/models/viXTTS', local_dir_use_symlinks=False)"

# Copy application code
COPY . .

# Create persistent directories
RUN mkdir -p reference_voices speaker_embeddings models_cache

# 2. FastText language-detection model (~131MB) — the lid.176.bin file
#    is COPY'd from models_cache/ (ensure .dockerignore does NOT exclude it).
#    If it's missing from your local tree, download it first:
#      python -c "import urllib.request; urllib.request.urlretrieve('https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin', 'models_cache/lid.176.bin')"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
