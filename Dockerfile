FROM python:3.11-slim

# System dependencies for VieNeu phonemizer (espeak-ng) and build tools
RUN apt-get update && apt-get install -y \
    espeak-ng \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

# Pre-download models on build (Optional, uncomment if needed)
# RUN python -c "from vieneu import Vieneu; Vieneu(mode='v3turbo', backend='onnx')"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
