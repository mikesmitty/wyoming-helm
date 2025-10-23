# Wyoming Whisper Helm Chart

This Helm chart deploys the [Wyoming Whisper](https://github.com/rhasspy/wyoming-whisper) speech-to-text service on Kubernetes. Wyoming Whisper provides fast, accurate speech recognition for Home Assistant voice assistants and other Wyoming protocol applications.

## Overview

This chart is optimized for **Home Assistant voice assistant** deployments with a focus on:
- **Low latency** - Fast response times for voice commands using efficient CPU-based models
- **Resource efficiency** - Smaller models (tiny, base) optimized for voice command recognition
- **Easy integration** - Direct Wyoming protocol support for Home Assistant

The chart deploys:
- **Wyoming Whisper** (`rhasspy/wyoming-whisper`) - OpenAI Whisper with Wyoming protocol support
- **Persistent Storage** - Optional PVC for caching downloaded models (recommended)
- **Health Checks** - Liveness and readiness probes for reliability

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Persistent storage (recommended for faster startup)

## Installation

### Install from OCI Registry (Recommended)

Install the latest release from GitHub Container Registry:

```bash
helm install my-whisper oci://ghcr.io/mikesmitty/wyoming-whisper
```

Install a specific version:

```bash
helm install my-whisper oci://ghcr.io/mikesmitty/wyoming-whisper --version 0.5.0
```

### Install from Source

For development or local testing:

```bash
git clone https://github.com/mikesmitty/wyoming-helm.git
cd wyoming-helm
helm install my-whisper ./charts/wyoming-whisper
```

### Custom Configuration

Create a values file for your environment (e.g., `production.yaml`, `homeassistant.yaml`):

```yaml
# Optimized for Home Assistant voice commands
# Use quantized model for faster response times
model: base-int8

# Specify language for better accuracy
language: en

# Lower beam size for faster voice command processing
beamSize: 1

# Use int8 compute for optimal CPU performance
computeType: int8

# Cache models locally for faster restarts
localFilesOnly: true

# Enable persistent storage (recommended)
persistence:
  enabled: true
  size: 2Gi

# Reasonable resources for voice assistant use
resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi
```

Install with custom values from OCI:

```bash
helm install my-whisper oci://ghcr.io/mikesmitty/wyoming-whisper -f production.yaml
```

Or from source:

```bash
helm install my-whisper ./charts/wyoming-whisper -f production.yaml
```

## Configuration

The following table lists the configurable parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Wyoming Whisper image repository | `rhasspy/wyoming-whisper` |
| `image.tag` | Image tag | `2.5.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `10300` |
| `model` | Whisper model to use | `base` |
| `language` | Language code (empty for auto-detect) | `""` |
| `beamSize` | Beam search size (0 for auto) | `5` |
| `device` | Device for inference (cpu, cuda, auto) | `cpu` |
| `computeType` | Compute type (default, int8, int8_float16, int16, float16, float32) | `default` |
| `initialPrompt` | Initial prompt for first transcription window | `""` |
| `localFilesOnly` | Don't check HuggingFace for updates | `false` |
| `debug` | Enable debug logging | `false` |
| `extraArgs` | Additional command line arguments | `[]` |
| `resources` | Resource limits and requests | `{}` |
| `persistence.enabled` | Enable persistent storage | `true` |
| `persistence.size` | PVC size | `5Gi` |
| `persistence.storageClass` | Storage class | `""` |
| `persistence.accessMode` | Access mode | `ReadWriteOnce` |
| `persistence.existingClaim` | Use existing PVC | `""` |
| `livenessProbe.enabled` | Enable liveness probe | `true` |
| `readinessProbe.enabled` | Enable readiness probe | `true` |
| `nodeSelector` | Node selector | `{}` |
| `tolerations` | Tolerations | `[]` |
| `affinity` | Affinity rules | `{}` |

## Available Whisper Models

Wyoming Whisper (using faster-whisper backend) supports the following models:

### Standard Multilingual Models
- `tiny` - Smallest model, fastest inference (~39M parameters, ~75MB)
- `base` - Small model, good balance (default) (~74M parameters, ~142MB)
- `small` - Medium model, better accuracy (~244M parameters, ~466MB)
- `medium` - Large model, high accuracy (~769M parameters, ~1.5GB)
- `large` - Very large model, highest accuracy (~1550M parameters, ~2.9GB)
- `large-v2` - Improved large model (~1550M parameters, ~2.9GB)
- `large-v3` - Latest large model (~1550M parameters, ~2.9GB)
- `large-v3-turbo` - Optimized large model for speed (~809M parameters, ~1.6GB)

### Quantized Models (INT8 - Faster with less memory)
- `tiny-int8` - Quantized tiny model
- `base-int8` - Quantized base model
- `small-int8` - Quantized small model
- `medium-int8` - Quantized medium model
- `distil-large-v3` - Distilled large model, faster inference

### English-Only Models
For better accuracy on English audio:
- `tiny.en` - Smallest English-only model
- `base.en` - Small English-only model
- `small.en` - Medium English-only model
- `medium.en` - Large English-only model

### HuggingFace Models
You can also use HuggingFace models directly:
- `Systran/faster-distil-whisper-small.en` - Distilled small English model
- `Systran/faster-whisper-large-v3` - Large v3 from HuggingFace
- Any compatible faster-whisper model from HuggingFace

### Model Selection Guide

**For Home Assistant Voice Commands:**
- **Recommended**: `base-int8` or `tiny-int8` - Fastest response, excellent for voice commands
- **Best balance**: `base` (default) - Good accuracy with reasonable latency
- **Ultra-fast**: `tiny` or `tiny-int8` - Lowest latency, good for simple commands
- **English-only**: Use `.en` variants (e.g., `base.en`) for better accuracy

**For Other Use Cases:**
- **Transcription quality priority**: `small` or `medium` - Better accuracy for longer audio
- **High-throughput processing**: `large-v3-turbo` with GPU acceleration
- **Best quality (not voice)**: `large-v3` - Highest accuracy for transcription workloads

**Key Recommendation:** For Home Assistant voice assistants, prioritize response time over absolute accuracy. Voice commands are typically short and don't require large models. Use `base-int8` or `tiny-int8` with `computeType: int8` for optimal performance.

**Note:** Models are automatically downloaded on first run. Using persistent storage is recommended to avoid re-downloading models after pod restarts.

### Resource Requirements by Model

| Model | Disk Space | Memory (approx) |
|-------|-----------|-----------------|
| tiny | ~75MB | ~1GB |
| base | ~142MB | ~1GB |
| small | ~466MB | ~2GB |
| medium | ~1.5GB | ~4GB |
| large/large-v2/large-v3 | ~2.9GB | ~8GB |
| large-v3-turbo | ~1.6GB | ~6GB |

## Usage

### Accessing the Wyoming Service

After installation, get connection details:

```bash
helm status my-whisper
```

For ClusterIP service (default), port-forward to access locally:

```bash
kubectl port-forward svc/my-whisper-wyoming-whisper 10300:10300
```

Then connect to `tcp://localhost:10300`

### Using with Home Assistant

Add to your Home Assistant `configuration.yaml`:

```yaml
wyoming:
  - platform: whisper
    host: my-whisper-wyoming-whisper.default.svc.cluster.local
    port: 10300
```

Or if exposed externally via LoadBalancer:

```yaml
wyoming:
  - platform: whisper
    host: <EXTERNAL_IP>
    port: 10300
```

### Command Line Testing

You can test the service using the Wyoming protocol client:

```bash
# Install wyoming client
pip install wyoming

# Test transcription
echo "Hello world" | \
  wyoming-client --uri tcp://localhost:10300
```

## Advanced Configuration

### Optimizing for Home Assistant Voice Response Time

For the fastest voice command processing:

```yaml
# Use quantized model for speed
model: base-int8

# Set compute type to int8 for CPU optimization
computeType: int8

# Lower beam size for faster decoding (1-3 for voice)
beamSize: 1

# Specify language to skip detection
language: en

# Cache models locally
localFilesOnly: true

# Minimal resources for voice commands
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 512Mi
```

### Optimizing Performance with Compute Types

Use INT8 quantization for faster CPU-based inference with minimal quality loss:

```yaml
# Use a quantized model
model: base-int8

# Set compute type to int8 (recommended for CPU)
computeType: int8
```

Available compute types:
- `default` - Automatic selection
- `int8` - 8-bit integer (fastest on CPU, minimal quality loss) **← Recommended**
- `int8_float16` - Mixed precision
- `int16` - 16-bit integer
- `float16` - 16-bit floating point (for GPU workloads)
- `float32` - 32-bit floating point (highest quality, slowest)

### Improving Accuracy with Initial Prompts

Provide context to improve transcription accuracy for specific use cases:

```yaml
# For Home Assistant voice commands (optional)
initialPrompt: "Home Assistant voice commands for smart home control"

# For specific domains
# initialPrompt: "Medical terminology and patient care instructions"
```

**Note:** For general Home Assistant voice use, an initial prompt is usually not necessary.

### Faster Startup with Cached Models

Avoid checking HuggingFace on every startup:

```yaml
# Enable local files only mode (recommended after first run)
localFilesOnly: true

# Ensure persistence is enabled to cache models
persistence:
  enabled: true
  size: 2Gi  # 2-5Gi depending on model size
```

### Debug Logging

Enable debug mode for troubleshooting:

```yaml
debug: true
```

### Complete Home Assistant Voice Example

Full configuration optimized for Home Assistant voice assistant:

```yaml
# Efficient model for voice commands
model: base-int8
language: en

# CPU optimization
device: cpu
computeType: int8
beamSize: 1  # Fast response for voice

# Cache models for quick startup
localFilesOnly: true
persistence:
  enabled: true
  size: 2Gi

# Minimal resources for voice workload
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 512Mi

# Internal service (accessed from Home Assistant)
service:
  type: ClusterIP
  port: 10300
```

### GPU Acceleration (Advanced - For High-Throughput Workloads)

**Note:** GPU acceleration is typically **not needed** for Home Assistant voice use. It's useful for high-throughput transcription workloads.

If you have GPU resources and need maximum throughput:

```yaml
# Set device to cuda
device: cuda
computeType: float16

# Request GPU resources
resources:
  limits:
    nvidia.com/gpu: 1
  requests:
    nvidia.com/gpu: 1

# Target GPU nodes
nodeSelector:
  gpu: "true"
```

GPU acceleration requires:
- NVIDIA GPU hardware
- NVIDIA device plugin for Kubernetes
- CUDA-compatible drivers installed

### Custom Arguments

Pass additional arguments via extraArgs if needed:

```yaml
extraArgs:
  - "--log-format"
  - "json"
```

## Troubleshooting

### View logs

```bash
kubectl logs -l app.kubernetes.io/name=wyoming-whisper
```

### Model download issues

If models are being re-downloaded on every restart:
- Ensure `persistence.enabled: true` in your values
- Check PVC is bound: `kubectl get pvc`

### Service not responding

Check pod status:
```bash
kubectl get pods -l app.kubernetes.io/name=wyoming-whisper
kubectl describe pod <pod-name>
```

Check if the readiness probe is passing:
```bash
kubectl get pods -l app.kubernetes.io/name=wyoming-whisper -o wide
```

### Out of memory errors

Larger models require more memory. Increase resource limits:

```yaml
resources:
  limits:
    memory: 8Gi
  requests:
    memory: 4Gi
```

## Uninstallation

To uninstall/delete the deployment:

```bash
helm uninstall my-whisper
```

To also delete the PVC:

```bash
kubectl delete pvc my-whisper-wyoming-whisper-data
```

## Upgrading

### To a newer chart version

From OCI registry:

```bash
helm upgrade my-whisper oci://ghcr.io/mikesmitty/wyoming-whisper --version 0.5.0
```

From source:

```bash
helm upgrade my-whisper ./charts/wyoming-whisper
```

### To change the model

From OCI registry:

```bash
helm upgrade my-whisper oci://ghcr.io/mikesmitty/wyoming-whisper \
  --set model=large-v3-turbo \
  --reuse-values
```

From source:

```bash
helm upgrade my-whisper ./charts/wyoming-whisper \
  --set model=large-v3-turbo \
  --reuse-values
```

## References

- [Wyoming Whisper](https://github.com/rhasspy/wyoming-whisper)
- [Wyoming Protocol](https://github.com/rhasspy/wyoming)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Home Assistant Wyoming Integration](https://www.home-assistant.io/integrations/wyoming/)
