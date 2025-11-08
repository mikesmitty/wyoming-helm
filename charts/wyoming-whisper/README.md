# Wyoming Whisper Helm Chart

[Wyoming Whisper](https://github.com/rhasspy/wyoming-whisper) provides fast, accurate speech-to-text for Home Assistant voice assistants using OpenAI's Whisper models with the Wyoming protocol.

## Quick Start

### Install from OCI Registry

```bash
helm install whisper oci://ghcr.io/mikesmitty/charts/wyoming-whisper
```

### Install with Custom Configuration

Create a `values.yaml` file:

```yaml
# For English language (recommended for better accuracy)
language: en

# Enable persistent storage to cache models
persistence:
  enabled: true
  size: 2Gi
```

Install the chart:

```bash
helm install whisper oci://ghcr.io/mikesmitty/charts/wyoming-whisper -f values.yaml
```

## Using with Home Assistant

After installation, add to your Home Assistant `configuration.yaml`:

```yaml
wyoming:
  - platform: whisper
    host: whisper-wyoming-whisper.default.svc.cluster.local
    port: 10300
```

**Note**: Replace `default` with your namespace if different, and `whisper` with your release name if different.

## Configuration

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `model` | Whisper model to use | `auto` (parakeet) |
| `language` | Language code (e.g., `en`, `de`, `fr`) | `auto` |
| `beamSize` | Beam search size (0 for auto) | `0` |
| `device` | Device for inference (`cpu`, `cuda`) | `cpu` |
| `computeType` | Compute type (`default`, `int8`, `float16`) | `default` |
| `sttLibrary` | STT library (`auto`, `faster-whisper`, `sherpa`) | `auto` |
| `cpuThreads` | Number of CPU threads | `4` |
| `localFilesOnly` | Don't check for model updates | `false` |
| `persistence.enabled` | Enable persistent storage | `true` |
| `persistence.size` | Storage size | `5Gi` |
| `resources` | CPU/Memory resource requests/limits | `{}` |

### Language Configuration

**Important**: Set the `language` parameter based on your use case:

- **English only**: Set `language: en` for better accuracy
- **Other single language**: Set to your language code (e.g., `de`, `fr`, `es`)
- **Multiple languages**: Leave as `language: auto` for automatic detection

Example for English:
```yaml
language: en
```

### Available Models

#### Whisper Models
- `auto` - Default, uses parakeet model (recommended for v3.0+)
- `tiny`, `base`, `small`, `medium`, `large` - Standard multilingual models
- `tiny-int8`, `base-int8`, `small-int8` - Quantized models (faster)
- `tiny.en`, `base.en`, `small.en` - English-only models

#### Parakeet Model (v3.0+)
- Default when using `model: auto`
- Optimized for performance and accuracy
- Recommended for most use cases

**Recommendation**: Use the default `auto` setting with appropriate `language` configuration for best results.

### Model Storage

Whisper models are automatically downloaded on first run. Enable persistent storage to avoid re-downloading:

```yaml
persistence:
  enabled: true
  size: 5Gi  # Adjust based on model size
```

Model sizes:
- tiny: ~75MB
- base: ~142MB
- small: ~466MB
- medium: ~1.5GB
- large: ~2.9GB

## Advanced Configuration

### Optimizing Performance

For faster transcription:

```yaml
model: auto  # Uses efficient parakeet model
language: en  # Set to your language for better accuracy
cpuThreads: 4  # Adjust based on your CPU
localFilesOnly: true  # Skip model update checks
```

### Resource Limits

Set appropriate resource limits:

```yaml
resources:
  limits:
    cpu: 2000m
    memory: 4Gi
  requests:
    cpu: 1000m
    memory: 2Gi
```

### GPU Acceleration

For CUDA-enabled GPUs:

```yaml
device: cuda
computeType: float16

resources:
  limits:
    nvidia.com/gpu: 1
  requests:
    nvidia.com/gpu: 1
```

## Troubleshooting

### View Logs

```bash
kubectl logs -l app.kubernetes.io/name=wyoming-whisper
```

### Check Service Status

```bash
kubectl get pods -l app.kubernetes.io/name=wyoming-whisper
kubectl get svc -l app.kubernetes.io/name=wyoming-whisper
```

### Models Not Persisting

Ensure persistence is enabled and PVC is bound:

```bash
kubectl get pvc
```

### Port Forward for Testing

```bash
kubectl port-forward svc/whisper-wyoming-whisper 10300:10300
```

Then test with Wyoming client:

```bash
pip install wyoming
echo "Hello world" | wyoming-client --uri tcp://localhost:10300
```

## Upgrading

```bash
helm upgrade whisper oci://ghcr.io/mikesmitty/charts/wyoming-whisper
```

## Uninstalling

```bash
helm uninstall whisper

# Optionally delete the PVC
kubectl delete pvc whisper-wyoming-whisper-data
```

## References

- [Wyoming Whisper](https://github.com/rhasspy/wyoming-whisper)
- [Wyoming Protocol](https://github.com/rhasspy/wyoming)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Home Assistant Wyoming Integration](https://www.home-assistant.io/integrations/wyoming/)
