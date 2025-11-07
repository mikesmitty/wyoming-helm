# syntax=docker/dockerfile:1

# Use UV with Python 3.11 (3.12 may have compatibility issues with nemo-toolkit)
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies for audio processing, Intel GPU support, and build tools
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    git \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml /app/

# Install Python dependencies using UV
# UV will automatically handle the git-based transformers dependency
RUN uv pip install --system --no-cache \
    torch \
    librosa \
    soundfile \
    numpy \
    huggingface-hub \
    wyoming \
    "git+https://github.com/huggingface/transformers.git" \
    && uv pip install --system --no-cache "nemo-toolkit[tts]"

# Install Intel Extension for PyTorch for XPU support (optional)
# Uncomment if building for Intel GPU
# RUN uv pip install --system --no-cache intel-extension-for-pytorch

# Runtime stage
FROM python:3.11-slim-bookworm

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set up application directory
WORKDIR /app

# Copy Wyoming server script
COPY wyoming_kanitts.py /app/

# Create data directory for model cache
RUN mkdir -p /data/huggingface && \
    chmod 755 /app/wyoming_kanitts.py

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/data/huggingface \
    TRANSFORMERS_CACHE=/data/huggingface \
    PYTORCH_DEVICE=cpu

# Expose Wyoming protocol port
EXPOSE 10220

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python3 -c "import socket; s = socket.socket(); s.connect(('localhost', 10220)); s.close()" || exit 1

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash kanitts && \
    chown -R kanitts:kanitts /app /data

USER kanitts

# Entrypoint
ENTRYPOINT ["python3", "/app/wyoming_kanitts.py"]

# Default arguments
CMD ["--uri", "tcp://0.0.0.0:10220"]
