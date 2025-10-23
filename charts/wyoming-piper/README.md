# Wyoming Piper Helm Chart

This Helm chart deploys the [Wyoming Piper](https://github.com/rhasspy/wyoming-piper) text-to-speech service on Kubernetes. Wyoming Piper provides fast, natural-sounding text-to-speech for Home Assistant voice assistants and other Wyoming protocol applications.

## Overview

This chart is optimized for **Home Assistant voice assistant** deployments with a focus on:
- **Natural speech** - High-quality voices with natural intonation
- **Low latency** - Fast text-to-speech generation for voice responses
- **Easy integration** - Direct Wyoming protocol support for Home Assistant

The chart deploys:
- **Wyoming Piper** (`rhasspy/wyoming-piper`) - Neural text-to-speech with Wyoming protocol support
- **Persistent Storage** - Optional PVC for caching downloaded voice models (recommended)
- **Health Checks** - Liveness and readiness probes for reliability

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Persistent storage (recommended for faster startup)

## Installation

### Install from OCI Registry (Recommended)

Install the latest release from GitHub Container Registry:

```bash
helm install my-piper oci://ghcr.io/mikesmitty/wyoming-piper
```

Install a specific version:

```bash
helm install my-piper oci://ghcr.io/mikesmitty/wyoming-piper --version 0.5.0
```

### Install from Source

For development or local testing:

```bash
git clone https://github.com/mikesmitty/wyoming-helm.git
cd wyoming-helm
helm install my-piper ./charts/wyoming-piper
```

### Custom Configuration

Create a values file for your environment (e.g., `production.yaml`, `homeassistant.yaml`):

```yaml
# Use a high-quality English voice
voice: en_US-lessac-high

# Enable streaming for lower latency
streaming: true

# Enable persistent storage (recommended)
persistence:
  enabled: true
  size: 2Gi

# Reasonable resources for TTS
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 512Mi
```

Install with custom values from OCI:

```bash
helm install my-piper oci://ghcr.io/mikesmitty/wyoming-piper -f production.yaml
```

Or from source:

```bash
helm install my-piper ./charts/wyoming-piper -f production.yaml
```

## Configuration

The following table lists the configurable parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Wyoming Piper image repository | `rhasspy/wyoming-piper` |
| `image.tag` | Image tag | `1.6.3` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `10200` |
| `voice` | Piper voice to use | `en_US-lessac-medium` |
| `speaker` | Speaker ID/name for multi-speaker voices | `""` |
| `noiseScale` | Generator noise (0.0-1.0) | `0.667` |
| `lengthScale` | Phoneme length scale (speed) | `1.0` |
| `noiseWScale` | Phoneme width noise | `0.333` |
| `autoPunctuation` | Auto-add punctuation | `".?!"` |
| `streaming` | Enable audio streaming | `true` |
| `samplesPerChunk` | Samples per audio chunk | `1024` |
| `updateVoices` | Update voices list on startup | `false` |
| `useCuda` | Enable CUDA GPU acceleration | `false` |
| `debug` | Enable debug logging | `false` |
| `extraArgs` | Additional command line arguments | `[]` |
| `resources` | Resource limits and requests | `{}` |
| `persistence.enabled` | Enable persistent storage | `true` |
| `persistence.size` | PVC size | `2Gi` |
| `persistence.storageClass` | Storage class | `""` |
| `persistence.accessMode` | Access mode | `ReadWriteOnce` |
| `persistence.existingClaim` | Use existing PVC | `""` |
| `livenessProbe.enabled` | Enable liveness probe | `true` |
| `readinessProbe.enabled` | Enable readiness probe | `true` |
| `nodeSelector` | Node selector | `{}` |
| `tolerations` | Tolerations | `[]` |
| `affinity` | Affinity rules | `{}` |

## Available Voices

Wyoming Piper supports a wide variety of voices in multiple languages and quality levels.

### Voice Quality Levels

- **low** - Fastest generation, lowest quality (~3-5MB per voice)
- **medium** - Balanced quality and speed (~10-20MB per voice) **← Recommended**
- **high** - Best quality, slower generation (~30-50MB per voice)
- **x-low** - Ultra-fast, minimal quality (some voices only)

### Popular English Voices

**US English:**
- `en_US-lessac-medium` - Male voice, clear and natural (default)
- `en_US-lessac-high` - High-quality version of lessac
- `en_US-libritts-high` - Multi-speaker, high quality
- `en_US-ryan-medium` - Male voice, energetic
- `en_US-amy-medium` - Female voice, clear

**UK English:**
- `en_GB-alan-medium` - Male British voice
- `en_GB-southern_english_female-medium` - Female British voice

### Other Languages

**German:**
- `de_DE-thorsten-medium` - Male German voice
- `de_DE-karlsson-low` - Fast German voice

**French:**
- `fr_FR-siwis-medium` - Female French voice
- `fr_FR-upmc-medium` - Male French voice

**Spanish:**
- `es_ES-sharvard-medium` - Male Spanish voice
- `es_MX-ald-medium` - Mexican Spanish

**Italian:**
- `it_IT-riccardo-medium` - Male Italian voice

**For a complete list of available voices**, visit:
- [Piper Voice Samples](https://rhasspy.github.io/piper-samples/)
- Voice format: `language_country-speaker-quality`

### Voice Selection Guide

**For Home Assistant Voice:**
- **Recommended**: `en_US-lessac-medium` (default) - Good balance
- **Best quality**: `en_US-lessac-high` or `en_US-libritts-high`
- **Fastest**: `en_US-lessac-low` or any `x-low` voice
- **Female voice**: `en_US-amy-medium`

**For multi-speaker scenarios:**
- Use `libritts` voices with `speaker` parameter to select different speakers
- Check voice documentation for available speaker IDs

## Usage

### Accessing the Wyoming Service

After installation, get connection details:

```bash
helm status my-piper
```

For ClusterIP service (default), port-forward to access locally:

```bash
kubectl port-forward svc/my-piper-wyoming-piper 10200:10200
```

Then connect to `tcp://localhost:10200`

### Using with Home Assistant

Add to your Home Assistant `configuration.yaml`:

```yaml
wyoming:
  - platform: piper
    host: my-piper-wyoming-piper.default.svc.cluster.local
    port: 10200
```

Or if exposed externally via LoadBalancer:

```yaml
wyoming:
  - platform: piper
    host: <EXTERNAL_IP>
    port: 10200
```

## Advanced Configuration

### Optimizing for Home Assistant Voice

For natural-sounding voice responses:

```yaml
# Use high-quality voice
voice: en_US-lessac-high

# Enable streaming for lower latency
streaming: true

# Adjust speech parameters
lengthScale: 1.0  # 1.0 = normal speed, >1.0 = slower, <1.0 = faster
noiseScale: 0.667  # Higher = more variable/natural
noiseWScale: 0.333  # Adds variation to phoneme duration

# Cache models for quick startup
persistence:
  enabled: true
  size: 2Gi

# Minimal resources for TTS
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 512Mi
```

### Adjusting Speech Speed

Control speaking rate with `lengthScale`:

```yaml
# Faster speech (80% speed)
lengthScale: 0.8

# Slower speech (120% speed)
lengthScale: 1.2

# Normal speed (default)
lengthScale: 1.0
```

### Using Multi-Speaker Voices

Some voices support multiple speakers:

```yaml
# Use libritts with specific speaker
voice: en_US-libritts-high
speaker: "p225"  # Female speaker
# or
speaker: "p226"  # Male speaker
```

### Faster Voice Model Download

Update voices list on startup:

```yaml
updateVoices: true
```

### Debug Logging

Enable debug mode for troubleshooting:

```yaml
debug: true
```

### Complete Home Assistant TTS Example

Full configuration optimized for Home Assistant:

```yaml
# High-quality natural voice
voice: en_US-lessac-high

# Enable streaming for responsiveness
streaming: true

# Natural speech parameters
lengthScale: 1.0
noiseScale: 0.667
noiseWScale: 0.333

# Cache models for fast startup
persistence:
  enabled: true
  size: 2Gi

# Efficient resources for TTS
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
  port: 10200
```

### GPU Acceleration (Advanced - Not Typically Needed)

**Note:** GPU acceleration is typically **not needed** for Home Assistant TTS. CPU performance is sufficient for real-time speech generation.

If you have specific high-throughput needs:

```yaml
# Enable CUDA (requires onnxruntime-gpu)
useCuda: true

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

## Troubleshooting

### View logs

```bash
kubectl logs -l app.kubernetes.io/name=wyoming-piper
```

### Voice model download issues

If models are being re-downloaded on every restart:
- Ensure `persistence.enabled: true` in your values
- Check PVC is bound: `kubectl get pvc`

### Service not responding

Check pod status:
```bash
kubectl get pods -l app.kubernetes.io/name=wyoming-piper
kubectl describe pod <pod-name>
```

### Testing TTS

You can test the service using the Wyoming protocol client:

```bash
# Install wyoming client
pip install wyoming

# Test TTS
echo "Hello from Piper" | \
  wyoming-client --uri tcp://localhost:10200 --type tts
```

### Audio quality issues

Try adjusting voice parameters:

```yaml
# More consistent speech
noiseScale: 0.5

# More natural/variable speech
noiseScale: 0.8

# Slower, clearer speech
lengthScale: 1.2
```

## Uninstallation

To uninstall/delete the deployment:

```bash
helm uninstall my-piper
```

To also delete the PVC:

```bash
kubectl delete pvc my-piper-wyoming-piper-data
```

## Upgrading

### To a newer chart version

From OCI registry:

```bash
helm upgrade my-piper oci://ghcr.io/mikesmitty/wyoming-piper --version 0.5.0
```

From source:

```bash
helm upgrade my-piper ./charts/wyoming-piper
```

### To change the voice

From OCI registry:

```bash
helm upgrade my-piper oci://ghcr.io/mikesmitty/wyoming-piper \
  --set voice=en_US-lessac-high \
  --reuse-values
```

From source:

```bash
helm upgrade my-piper ./charts/wyoming-piper \
  --set voice=en_US-lessac-high \
  --reuse-values
```

## References

- [Wyoming Piper](https://github.com/rhasspy/wyoming-piper)
- [Piper TTS](https://github.com/rhasspy/piper)
- [Wyoming Protocol](https://github.com/rhasspy/wyoming)
- [Piper Voice Samples](https://rhasspy.github.io/piper-samples/)
- [Home Assistant Wyoming Integration](https://www.home-assistant.io/integrations/wyoming/)
