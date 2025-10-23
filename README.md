# Wyoming Helm Charts

Helm charts for deploying [Wyoming Protocol](https://github.com/rhasspy/wyoming) services on Kubernetes, optimized for Home Assistant voice assistants.

## Available Charts

All charts are published to GitHub Container Registry (GHCR) as OCI artifacts.

### Wyoming Whisper - Speech-to-Text
Fast, accurate speech recognition for Home Assistant voice assistants.

- **Chart**: `oci://ghcr.io/mikesmitty/wyoming-whisper`
- **Source**: `charts/wyoming-whisper`
- **Image**: `rhasspy/wyoming-whisper`
- **Default Port**: 10300
- **Use Case**: Voice command recognition, speech-to-text
- **Recommended Model**: `base-int8` (fast response, good accuracy)

[📖 Whisper Chart Documentation](charts/wyoming-whisper/README.md)

### Wyoming Piper - Text-to-Speech
Natural-sounding text-to-speech for Home Assistant voice responses.

- **Chart**: `oci://ghcr.io/mikesmitty/wyoming-piper`
- **Source**: `charts/wyoming-piper`
- **Image**: `rhasspy/wyoming-piper`
- **Default Port**: 10200
- **Use Case**: Voice responses, text-to-speech
- **Recommended Voice**: `en_US-lessac-medium` (natural, balanced)

[📖 Piper Chart Documentation](charts/wyoming-piper/README.md)

## Quick Start

### Install from OCI Registry (Recommended)

Install both charts for a complete voice assistant:

```bash
# Install speech-to-text (Whisper)
helm install whisper oci://ghcr.io/mikesmitty/wyoming-whisper

# Install text-to-speech (Piper)
helm install piper oci://ghcr.io/mikesmitty/wyoming-piper
```

Install specific versions:

```bash
# Install Whisper with specific version
helm install whisper oci://ghcr.io/mikesmitty/wyoming-whisper --version 1.0.0

# Install Piper with specific version
helm install piper oci://ghcr.io/mikesmitty/wyoming-piper --version 1.0.0
```

### Install from Source

For development or local testing:

```bash
# Clone the repository
git clone https://github.com/mikesmitty/wyoming-helm.git
cd wyoming-helm

# Install speech-to-text (Whisper)
helm install whisper ./charts/wyoming-whisper

# Install text-to-speech (Piper)
helm install piper ./charts/wyoming-piper
```

## Home Assistant Integration

After installing both charts, add to your Home Assistant `configuration.yaml`:

```yaml
# Wyoming Protocol Integration
wyoming:
  # Speech-to-text (Whisper)
  - platform: whisper
    host: whisper-wyoming-whisper.default.svc.cluster.local
    port: 10300

  # Text-to-speech (Piper)
  - platform: piper
    host: piper-wyoming-piper.default.svc.cluster.local
    port: 10200
```

## Optimized for Home Assistant Voice

Both charts are specifically tuned for Home Assistant voice assistant deployments:

### Wyoming Whisper (STT)
- ✅ CPU-optimized models (base, base-int8)
- ✅ Fast response times for voice commands
- ✅ Low resource usage (250m CPU, 512Mi RAM)
- ✅ Persistent model caching

### Wyoming Piper (TTS)
- ✅ Natural-sounding voices
- ✅ Streaming audio for low latency
- ✅ Multiple language support
- ✅ Adjustable speech parameters

## Configuration Examples

### Optimized for Fast Response

**Whisper (STT):**
```yaml
model: base-int8
language: en
beamSize: 1
computeType: int8
localFilesOnly: true
```

**Piper (TTS):**
```yaml
voice: en_US-lessac-medium
streaming: true
lengthScale: 1.0
```

### Optimized for Quality

**Whisper (STT):**
```yaml
model: large-v3-turbo
language: en
beamSize: 5
```

**Piper (TTS):**
```yaml
voice: en_US-lessac-high
noiseScale: 0.667
lengthScale: 1.0
```

## Features

- **Wyoming Protocol Native** - Direct protocol support for Home Assistant
- **Persistent Storage** - Cache models for faster pod restarts
- **Health Checks** - Liveness and readiness probes for reliability
- **Security Hardened** - Non-root containers, dropped capabilities, seccomp profiles
- **Resource Efficient** - Optimized for CPU-based inference
- **Production Ready** - Configurable resource limits, node selectors, tolerations

## Requirements

- Kubernetes 1.19+
- Helm 3.0+
- Persistent storage (recommended)
- For GPU acceleration: NVIDIA GPU with device plugin (optional)

## Chart Versioning and Releases

This repository uses [Release Please](https://github.com/googleapis/release-please) for automated versioning and changelog generation. Each chart is versioned independently:

- Charts are tagged as: `wyoming-whisper-v1.0.0`, `wyoming-piper-v1.0.0`
- Releases are automatically published to GitHub Container Registry (GHCR) as OCI artifacts
- Changelogs are maintained in each chart's directory

### Finding Available Versions

Browse published charts on GitHub Container Registry:

- **Whisper**: https://github.com/mikesmitty/wyoming-helm/pkgs/container/wyoming-whisper
- **Piper**: https://github.com/mikesmitty/wyoming-helm/pkgs/container/wyoming-piper

Or use Helm to show available versions:

```bash
# Show Wyoming Whisper versions
helm show chart oci://ghcr.io/mikesmitty/wyoming-whisper

# Show Wyoming Piper versions
helm show chart oci://ghcr.io/mikesmitty/wyoming-piper
```

View chart values before installing:

```bash
# Show default values for Wyoming Whisper
helm show values oci://ghcr.io/mikesmitty/wyoming-whisper

# Show default values for Wyoming Piper
helm show values oci://ghcr.io/mikesmitty/wyoming-piper
```

## Development

### Linting Charts

```bash
# Lint all charts
helm lint charts/wyoming-whisper
helm lint charts/wyoming-piper
```

### Testing Charts

```bash
# Test template rendering
helm template test charts/wyoming-whisper
helm template test charts/wyoming-piper

# Install locally for testing
helm install test-whisper charts/wyoming-whisper --dry-run
helm install test-piper charts/wyoming-piper --dry-run
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `helm lint` and `helm template`
5. Submit a pull request

## References

- [Wyoming Protocol](https://github.com/rhasspy/wyoming)
- [Wyoming Whisper](https://github.com/rhasspy/wyoming-whisper)
- [Wyoming Piper](https://github.com/rhasspy/wyoming-piper)
- [Home Assistant Wyoming Integration](https://www.home-assistant.io/integrations/wyoming/)
- [Piper Voice Samples](https://rhasspy.github.io/piper-samples/)

## License

See individual chart directories for licensing information.

## Support

For issues and questions:
- Chart issues: Open an issue in this repository
- Wyoming Protocol: [Wyoming GitHub](https://github.com/rhasspy/wyoming)
- Home Assistant Integration: [Home Assistant Community](https://community.home-assistant.io/)
