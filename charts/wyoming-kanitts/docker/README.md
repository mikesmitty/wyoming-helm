# Wyoming KaniTTS Docker Image

Docker image for running [KaniTTS](https://github.com/nineninesix-ai/kani-tts) as a Wyoming protocol TTS server **optimized for Intel GPUs**.

## Features

- **Intel XPU (GPU) acceleration** via PyTorch 2.7+ native support
- KaniTTS high-quality neural TTS (370M/450M parameters)
- Wyoming protocol for Home Assistant integration
- Supports Intel Arc, Iris Xe, and integrated GPUs
- Automatic CPU fallback
- Pre-configured for optimal Intel GPU performance

**Note:** This image is specifically built for Intel GPUs using PyTorch 2.7+ native XPU support. CUDA/NVIDIA GPUs are not supported.

## Quick Start

### With Intel GPU (Recommended)

```bash
docker run -p 10220:10220 \
  -v kanitts-data:/data \
  --device=/dev/dri \
  ghcr.io/mikesmitty/wyoming-kanitts:latest
```

The image defaults to Intel XPU mode with optimal settings pre-configured.

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
    devices:
      - /dev/dri:/dev/dri
    volumes:
      - kanitts-data:/data
    group_add:
      - video
      - render

volumes:
  kanitts-data:
```

## Home Assistant Integration

Add to your Home Assistant `configuration.yaml`:

```yaml
wyoming:
  - platform: tts
    host: <container-ip>
    port: 10220
```

Or configure in the UI:
1. Settings → Devices & Services
2. Add Integration → Wyoming Protocol
3. Enter host: `<container-ip>` and port: `10220`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTORCH_DEVICE` | `xpu` | Device: `xpu` (Intel GPU) or `cpu` |
| `KANITTS_MODEL` | `nineninesix/kani-tts-370m` | Model name |
| `ONEAPI_DEVICE_SELECTOR` | `level_zero:0` | Intel GPU selector |
| `HF_HOME` | `/data/huggingface` | Model cache directory |

## Model Options

### KaniTTS-370M (Default)
- **Size**: ~1.5GB
- **Memory**: ~2GB VRAM
- **Speed**: Fast
- **Quality**: High

### KaniTTS-450M
```bash
docker run -p 10220:10220 \
  -v kanitts-data:/data \
  --device=/dev/dri \
  -e KANITTS_MODEL=nineninesix/kani-tts-450m-0.1-pt \
  ghcr.io/mikesmitty/wyoming-kanitts:latest
```
- **Size**: ~1.8GB
- **Memory**: ~3GB VRAM
- **Speed**: Moderate
- **Quality**: Very High

## Volume Mounts

### `/data` - Model Cache
Persistent storage for downloaded models. **Recommended**: 5-10GB

## Troubleshooting

### Intel GPU Not Detected

Verify GPU access:

```bash
# Check devices
docker exec -it wyoming-kanitts ls -la /dev/dri

# Check PyTorch XPU
docker exec -it wyoming-kanitts python3 -c "import torch; print('XPU available:', torch.xpu.is_available())"
```

Ensure:
1. Intel GPU drivers installed on host (i915 or xe kernel driver)
2. Container has access to `/dev/dri`
3. User is in `render` and `video` groups

### Model Download Issues

```bash
# Check logs
docker logs wyoming-kanitts

# Manually download model
docker exec -it wyoming-kanitts python3 -c "from huggingface_hub import snapshot_download; snapshot_download('nineninesix/kani-tts-370m')"
```

### Connection Issues

```bash
# Test Wyoming protocol
pip install wyoming
echo "Hello from KaniTTS" | wyoming-client --uri tcp://localhost:10220 --type tts

# Check port
nc -zv localhost 10220
```

## Performance

### Intel Arc A770
- First synthesis: ~2-3s (includes model loading)
- Subsequent: ~0.5-1s per sentence

### Intel Iris Xe (integrated)
- First synthesis: ~3-4s
- Subsequent: ~1-2s per sentence

### CPU Fallback (Intel i7-12700K)
- First synthesis: ~3-5s
- Subsequent: ~1-2s per sentence

**Note**: Performance varies based on text length and model size.

## Security

The container runs as non-root user `kanitts` (UID 1000) for security.

## License

- KaniTTS: [Apache 2.0](https://github.com/nineninesix-ai/kani-tts/blob/main/LICENSE)
- Wyoming Protocol: [MIT](https://github.com/rhasspy/wyoming/blob/master/LICENSE)
- PyTorch: [BSD](https://github.com/pytorch/pytorch/blob/master/LICENSE)

## References

- [KaniTTS](https://github.com/nineninesix-ai/kani-tts)
- [Wyoming Protocol](https://github.com/rhasspy/wyoming)
- [Home Assistant Wyoming Integration](https://www.home-assistant.io/integrations/wyoming/)
- [PyTorch Intel GPU Support](https://pytorch.org/blog/intel-gpu-support-pytorch-2-5/)
