# Building Wyoming KaniTTS

Quick guide for building and testing the Wyoming KaniTTS Docker image.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- For Intel GPU: Intel GPU drivers on host
- For NVIDIA GPU: nvidia-docker runtime

## Quick Build & Test

### 1. Build the Image

```bash
cd docker/wyoming-kanitts
docker build -t wyoming-kanitts:local .
```

**Build time**: ~5-10 minutes (depending on network speed for Python packages)

### 2. Test CPU Version

```bash
# Start the container
docker run -d \
  --name kanitts-test \
  -p 10220:10220 \
  -v kanitts-test-data:/data \
  wyoming-kanitts:local

# Check logs
docker logs -f kanitts-test

# Test Wyoming protocol
pip install wyoming
echo "Hello from KaniTTS" | wyoming-client --uri tcp://localhost:10220 --type tts

# Stop and remove
docker stop kanitts-test
docker rm kanitts-test
```

### 3. Test with Docker Compose

```bash
# CPU version
docker compose up -d
docker compose logs -f

# Intel GPU version
docker compose -f docker-compose.intel-gpu.yml up -d
docker compose -f docker-compose.intel-gpu.yml logs -f

# NVIDIA GPU version
docker compose -f docker-compose.nvidia-gpu.yml up -d
docker compose -f docker-compose.nvidia-gpu.yml logs -f

# Stop
docker compose down
```

## Verifying GPU Support

### Intel XPU

```bash
docker exec -it wyoming-kanitts python3 -c "
import torch
print('XPU available:', torch.xpu.is_available())
print('XPU device count:', torch.xpu.device_count() if torch.xpu.is_available() else 0)
"
```

Expected output:
```
XPU available: True
XPU device count: 1
```

### NVIDIA CUDA

```bash
docker exec -it wyoming-kanitts python3 -c "
import torch
print('CUDA available:', torch.cuda.is_available())
print('CUDA device count:', torch.cuda.device_count())
print('CUDA device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')
"
```

Expected output:
```
CUDA available: True
CUDA device count: 1
CUDA device: NVIDIA GeForce RTX 3080
```

## Building for Production

### Multi-Platform Build

```bash
# Create buildx builder
docker buildx create --name mybuilder --use
docker buildx inspect --bootstrap

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/mikesmitty/wyoming-kanitts:latest \
  -t ghcr.io/mikesmitty/wyoming-kanitts:0.1.0 \
  --push \
  .
```

### With Intel XPU Support

1. Edit `Dockerfile`, uncomment:
   ```dockerfile
   RUN uv pip install --system --no-cache intel-extension-for-pytorch
   ```

2. Build with tag:
   ```bash
   docker build -t ghcr.io/mikesmitty/wyoming-kanitts:intel-xpu .
   ```

### GitHub Actions CI/CD

Create `.github/workflows/docker-build.yml`:

```yaml
name: Build Docker Image

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Docker meta
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository_owner }}/wyoming-kanitts
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./docker/wyoming-kanitts
          platforms: linux/amd64,linux/arm64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Troubleshooting Build Issues

### UV Installation Fails

If UV fails to install dependencies:

```dockerfile
# Try with pip fallback
RUN uv pip install --system --no-cache torch || pip install torch
```

### Transformers Git Install Issues

If git-based transformers fails:

```bash
# Build with specific commit
docker build --build-arg TRANSFORMERS_COMMIT=main .
```

Update Dockerfile:
```dockerfile
ARG TRANSFORMERS_COMMIT=main
RUN uv pip install --system "git+https://github.com/huggingface/transformers.git@${TRANSFORMERS_COMMIT}"
```

### nemo-toolkit Installation Issues

If nemo-toolkit fails on ARM:

```dockerfile
# Skip on ARM builds
RUN if [ "$(uname -m)" = "x86_64" ]; then \
      uv pip install --system "nemo-toolkit[tts]"; \
    fi
```

### Image Size Too Large

Check layer sizes:
```bash
docker history wyoming-kanitts:local

# Use dive for analysis
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  wagoodman/dive:latest wyoming-kanitts:local
```

Optimize by:
- Using multi-stage builds (already implemented)
- Combining RUN commands
- Cleaning apt cache (already done)
- Using slim base images (already using slim)

## Testing Integration with Home Assistant

### Using Docker Network

```bash
# Create network
docker network create homeassistant

# Run Wyoming KaniTTS
docker run -d \
  --name wyoming-kanitts \
  --network homeassistant \
  -v kanitts-data:/data \
  wyoming-kanitts:local

# Run Home Assistant (example)
docker run -d \
  --name homeassistant \
  --network homeassistant \
  -p 8123:8123 \
  homeassistant/home-assistant:latest
```

In Home Assistant `configuration.yaml`:
```yaml
wyoming:
  - platform: tts
    host: wyoming-kanitts
    port: 10220
```

## Performance Testing

### Benchmark Synthesis Time

```bash
docker exec -it wyoming-kanitts python3 -c "
import time
from kani_tts import KaniTTS
import torch

device = 'cpu'  # or 'cuda', 'xpu'
model = KaniTTS('nineninesix/kani-tts-370m').to(device)

text = 'The quick brown fox jumps over the lazy dog.'

# Warmup
model.generate(text)

# Benchmark
start = time.time()
for i in range(10):
    audio = model.generate(text)
end = time.time()

print(f'Average time per synthesis: {(end - start) / 10:.2f}s')
"
```

### Memory Usage

```bash
docker stats wyoming-kanitts --no-stream
```

## Next Steps

1. ✅ Build image locally
2. ✅ Test CPU version
3. 🔲 Test Intel GPU version (if available)
4. 🔲 Test NVIDIA GPU version (if available)
5. 🔲 Verify KaniTTS API matches implementation
6. 🔲 Test with Home Assistant
7. 🔲 Set up CI/CD pipeline
8. 🔲 Push to GHCR

## Important Notes

⚠️ **KaniTTS API Verification Required**

The current implementation assumes:
```python
audio = model.generate(text, sample_rate=24000)
```

Check the actual KaniTTS API and update `wyoming_kanitts.py` accordingly.

⚠️ **Python Version**

Using Python 3.11 for maximum compatibility. Python 3.12 may have issues with nemo-toolkit.

⚠️ **Model Download**

First run will download ~1.5GB model. Ensure:
- Persistent volume is mounted
- Sufficient disk space
- Internet connectivity
