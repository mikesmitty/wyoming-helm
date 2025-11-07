# Wyoming KaniTTS Docker Image

Docker image for running [KaniTTS](https://github.com/nineninesix-ai/kani-tts) as a Wyoming protocol TTS server with Intel XPU support.

## Features

- KaniTTS high-quality neural TTS
- Wyoming protocol for Home Assistant integration
- Intel XPU (GPU) support via PyTorch
- NVIDIA CUDA support
- CPU fallback
- UV for fast dependency management
- Multi-stage build for smaller image size

## Quick Start

### CPU Only

```bash
docker run -p 10220:10220 \
  -v kanitts-data:/data \
  ghcr.io/mikesmitty/wyoming-kanitts:latest
```

### With Intel GPU (XPU)

```bash
docker run -p 10220:10220 \
  -v kanitts-data:/data \
  --device=/dev/dri \
  -e PYTORCH_DEVICE=xpu \
  -e ONEAPI_DEVICE_SELECTOR=level_zero:0 \
  ghcr.io/mikesmitty/wyoming-kanitts:latest
```

### With NVIDIA GPU

```bash
docker run -p 10220:10220 \
  -v kanitts-data:/data \
  --gpus all \
  -e PYTORCH_DEVICE=cuda \
  ghcr.io/mikesmitty/wyoming-kanitts:latest
```

## Building the Image

### Standard Build (CPU/CUDA)

```bash
cd docker/wyoming-kanitts
docker build -t wyoming-kanitts:latest .
```

### Build with Intel XPU Support

Uncomment the Intel Extension for PyTorch line in the Dockerfile:

```dockerfile
# Install Intel Extension for PyTorch for XPU support (optional)
RUN uv pip install --system --no-cache intel-extension-for-pytorch
```

Then build:

```bash
docker build -t wyoming-kanitts:intel-xpu .
```

### Multi-platform Build

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/mikesmitty/wyoming-kanitts:latest \
  --push \
  .
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTORCH_DEVICE` | `cpu` | PyTorch device: `cpu`, `cuda`, or `xpu` |
| `KANITTS_MODEL` | `nineninesix/kani-tts-370m` | Hugging Face model name |
| `KANITTS_MODEL_REVISION` | `main` | Model branch/revision |
| `ONEAPI_DEVICE_SELECTOR` | `level_zero:0` | Intel GPU selector (XPU only) |
| `HF_HOME` | `/data/huggingface` | Hugging Face cache directory |
| `TRANSFORMERS_CACHE` | `/data/huggingface` | Transformers cache directory |

## Command Line Arguments

```bash
python3 wyoming_kanitts.py --help

Options:
  --uri URI              Server URI (required, e.g., tcp://0.0.0.0:10220)
  --model MODEL          KaniTTS model name from Hugging Face
  --device DEVICE        PyTorch device: cpu, cuda, xpu
  --sample-rate RATE     Audio sample rate in Hz (default: 24000)
  --debug                Enable debug logging
```

## Usage Examples

### With Custom Model

```bash
docker run -p 10220:10220 \
  -v kanitts-data:/data \
  -e KANITTS_MODEL=nineninesix/kani-tts-450m-0.1-pt \
  ghcr.io/mikesmitty/wyoming-kanitts:latest
```

### With Debug Logging

```bash
docker run -p 10220:10220 \
  -v kanitts-data:/data \
  ghcr.io/mikesmitty/wyoming-kanitts:latest \
  --uri tcp://0.0.0.0:10220 \
  --debug
```

### Docker Compose

```yaml
version: '3.8'

services:
  wyoming-kanitts:
    image: ghcr.io/mikesmitty/wyoming-kanitts:latest
    container_name: wyoming-kanitts
    restart: unless-stopped
    ports:
      - "10220:10220"
    volumes:
      - kanitts-data:/data
    environment:
      PYTORCH_DEVICE: cpu
      KANITTS_MODEL: nineninesix/kani-tts-370m
    healthcheck:
      test: ["CMD", "python3", "-c", "import socket; s = socket.socket(); s.connect(('localhost', 10220)); s.close()"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

volumes:
  kanitts-data:
```

### Docker Compose with Intel GPU

```yaml
version: '3.8'

services:
  wyoming-kanitts:
    image: ghcr.io/mikesmitty/wyoming-kanitts:intel-xpu
    container_name: wyoming-kanitts
    restart: unless-stopped
    ports:
      - "10220:10220"
    devices:
      - /dev/dri:/dev/dri
    volumes:
      - kanitts-data:/data
    environment:
      PYTORCH_DEVICE: xpu
      ONEAPI_DEVICE_SELECTOR: level_zero:0
      KANITTS_MODEL: nineninesix/kani-tts-370m
    group_add:
      - video
      - render

volumes:
  kanitts-data:
```

## Home Assistant Integration

After starting the container, add to your Home Assistant `configuration.yaml`:

```yaml
wyoming:
  - platform: tts
    host: <container-ip>
    port: 10220
```

Then configure in Home Assistant:
1. Go to Settings → Devices & Services
2. Add Integration → Wyoming Protocol
3. Enter host and port
4. Select KaniTTS as your TTS provider

## Model Selection

### KaniTTS-370M (Default)
- **Model**: `nineninesix/kani-tts-370m`
- **Size**: ~1.5GB
- **Memory**: ~2GB RAM/VRAM
- **Speed**: Fast
- **Quality**: High

### KaniTTS-450M
- **Model**: `nineninesix/kani-tts-450m-0.1-pt`
- **Size**: ~1.8GB
- **Memory**: ~3GB RAM/VRAM
- **Speed**: Moderate
- **Quality**: Very High

## Volume Mounts

### `/data` - Model Cache
Persistent storage for downloaded models. Recommended to avoid re-downloading on container restart.

**Size recommendation**: 5-10GB

## Troubleshooting

### Model Download Issues

If models fail to download:

```bash
# Check logs
docker logs wyoming-kanitts

# Manually download model
docker exec -it wyoming-kanitts bash
python3 -c "from huggingface_hub import snapshot_download; snapshot_download('nineninesix/kani-tts-370m')"
```

### Intel GPU Not Detected

Verify GPU access:

```bash
# Check devices
docker exec -it wyoming-kanitts ls -la /dev/dri

# Check PyTorch XPU
docker exec -it wyoming-kanitts python3 -c "import torch; print('XPU available:', torch.xpu.is_available())"
```

Ensure:
1. Intel GPU drivers installed on host
2. Container has access to `/dev/dri`
3. User is in `render` and `video` groups
4. Intel Extension for PyTorch is installed in image

### CUDA Not Found

```bash
# Check CUDA availability
docker exec -it wyoming-kanitts python3 -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

For NVIDIA GPU, use `--gpus all` flag or `nvidia-docker` runtime.

### Memory Issues

If you encounter OOM errors:
1. Use smaller model (370M instead of 450M)
2. Increase Docker memory limits
3. Use CPU instead of GPU for lower memory usage

### Connection Issues

```bash
# Test Wyoming protocol
pip install wyoming
echo "Hello from KaniTTS" | wyoming-client --uri tcp://localhost:10220 --type tts

# Check if port is open
nc -zv localhost 10220
```

## Performance

### CPU (Intel i7-12700K)
- First synthesis: ~3-5s (model loading)
- Subsequent: ~1-2s per sentence

### Intel GPU (Arc A770)
- First synthesis: ~2-3s (model loading)
- Subsequent: ~0.5-1s per sentence

### NVIDIA GPU (RTX 3080)
- First synthesis: ~1-2s (model loading)
- Subsequent: ~0.3-0.5s per sentence

**Note**: Times vary based on text length and model size.

## Development

### Local Testing

```bash
# Build image
docker build -t wyoming-kanitts:dev .

# Run with debug
docker run -it --rm \
  -p 10220:10220 \
  -v $(pwd)/data:/data \
  wyoming-kanitts:dev \
  --uri tcp://0.0.0.0:10220 \
  --debug

# Test from another terminal
echo "Testing KaniTTS" | wyoming-client --uri tcp://localhost:10220 --type tts
```

### Modify the Script

1. Edit `wyoming_kanitts.py`
2. Rebuild image
3. Test changes

## Security

The container runs as non-root user `kanitts` (UID 1000) with:
- Dropped capabilities
- Read-only root filesystem (when possible)
- No privilege escalation
- Seccomp profile

## License

This Docker image uses:
- KaniTTS: [Apache 2.0](https://github.com/nineninesix-ai/kani-tts/blob/main/LICENSE)
- Wyoming Protocol: [MIT](https://github.com/rhasspy/wyoming/blob/master/LICENSE)
- PyTorch: [BSD](https://github.com/pytorch/pytorch/blob/master/LICENSE)

## References

- [KaniTTS](https://github.com/nineninesix-ai/kani-tts)
- [Wyoming Protocol](https://github.com/rhasspy/wyoming)
- [Home Assistant Wyoming Integration](https://www.home-assistant.io/integrations/wyoming/)
- [UV Package Manager](https://github.com/astral-sh/uv)
