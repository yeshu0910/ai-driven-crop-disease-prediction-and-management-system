FROM python:3.11-slim AS base

LABEL maintainer="team@example.com"
LABEL description="AI-Driven Crop Disease Prediction and Management System"

# Install system dependencies for OpenCV, TensorFlow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

# Copy application code
COPY crop_disease_ai/ ./crop_disease_ai/

# Create necessary directories
RUN mkdir -p /app/logs /app/models /app/data /app/crop_disease_ai/models

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/')" || exit 1

CMD ["streamlit", "run", "crop_disease_ai/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
