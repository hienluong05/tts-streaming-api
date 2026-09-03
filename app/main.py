import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Create necessary directories
os.makedirs(settings.reference_voices_dir, exist_ok=True)
os.makedirs(settings.speaker_embeddings_dir, exist_ok=True)
os.makedirs(settings.models_cache_dir, exist_ok=True)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Vietnamese Text-to-Speech Streaming API with Voice Cloning"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.version}

from app.api.routes import router as api_router
app.include_router(api_router, prefix="/api/v1")
