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
# PyTorch 2.7+ has native Intel GPU support, no extensions needed
RUN uv pip install --system --no-cache \
    torch \
    librosa \
    soundfile \
    numpy \
    huggingface-hub \
    wyoming \
    "git+https://github.com/huggingface/transformers.git" \
    && uv pip install --system --no-cache "nemo-toolkit[tts]"

# Runtime stage
FROM python:3.11-slim-bookworm

# Install runtime dependencies including Intel GPU compute runtime
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    wget \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# Install Intel GPU compute runtime for XPU support
# Add Intel GPU repository and install compute runtime
RUN wget -qO - https://repositories.intel.com/gpu/intel-graphics.key | gpg --dearmor --output /usr/share/keyrings/intel-graphics.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/intel-graphics.gpg] https://repositories.intel.com/gpu/ubuntu jammy client" | \
    tee /etc/apt/sources.list.d/intel-gpu-jammy.list && \
    apt-get update && \
    apt-get install -y \
    intel-opencl-icd \
    intel-level-zero-gpu \
    level-zero \
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

# Environment variables for Intel XPU
ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/data/huggingface \
    TRANSFORMERS_CACHE=/data/huggingface \
    PYTORCH_DEVICE=xpu \
    ONEAPI_DEVICE_SELECTOR=level_zero:0 \
    PYTORCH_ENABLE_XPU=1

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
