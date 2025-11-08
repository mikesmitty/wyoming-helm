# syntax=docker/dockerfile:1

# Use Intel oneAPI runtime as base image
FROM intel/oneapi-runtime:2025.3.0-0-devel-ubuntu24.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    libsndfile1 \
    ffmpeg \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set up application directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Install the project's dependencies using the lockfile and settings
COPY pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Copy Wyoming server script
# Installing separately from its dependencies allows optimal layer caching
COPY wyoming_kanitts.py /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

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

# Create non-root user
RUN chown ubuntu:ubuntu /app /data

USER ubuntu

# Entrypoint
ENTRYPOINT ["uv", "run", "--no-sync", "--frozen", "/app/wyoming_kanitts.py"]

# Default arguments
CMD ["--uri", "tcp://0.0.0.0:10220"]
