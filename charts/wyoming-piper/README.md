# Wyoming Piper Helm Chart

[Wyoming Piper](https://github.com/rhasspy/wyoming-piper) provides fast, natural-sounding text-to-speech for Home Assistant voice assistants using neural voices with the Wyoming protocol.

## Quick Start

### Install from OCI Registry

```bash
helm install piper oci://ghcr.io/mikesmitty/charts/wyoming-piper
```

### Install with Custom Configuration

Create a `values.yaml` file:

```yaml
# Use a high-quality English voice
voice: en_US-lessac-high

# Enable persistent storage to cache voice models
persistence:
  enabled: true
  size: 2Gi
```

Install the chart:

```bash
helm install piper oci://ghcr.io/mikesmitty/charts/wyoming-piper -f values.yaml
```

## Using with Home Assistant

After installation, add to your Home Assistant `configuration.yaml`:

```yaml
wyoming:
  - platform: piper
    host: piper-wyoming-piper.default.svc.cluster.local
    port: 10200
```

**Note**: Replace `default` with your namespace if different, and `piper` with your release name if different.

## Configuration

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `voice` | Piper voice to use | `en_US-lessac-medium` |
| `speaker` | Speaker ID for multi-speaker voices | `""` |
| `streaming` | Enable audio streaming | `true` |
| `lengthScale` | Speaking speed (1.0 = normal) | `1.0` |
| `noiseScale` | Voice variation (0.0-1.0) | `0.667` |
| `noiseWScale` | Phoneme width noise | `0.333` |
| `updateVoices` | Update voices on startup | `false` |
| `persistence.enabled` | Enable persistent storage | `true` |
| `persistence.size` | Storage size | `2Gi` |
| `resources` | CPU/Memory resource requests/limits | `{}` |

### Voice Selection

Piper supports many voices in multiple languages and quality levels:

**Quality Levels:**
- `low` - Fast, lower quality (~3-5MB)
- `medium` - Balanced quality/speed (~10-20MB) - **Recommended**
- `high` - Best quality, slower (~30-50MB)

**Popular English Voices:**
- `en_US-lessac-medium` - Male, clear and natural (default)
- `en_US-lessac-high` - High-quality version
- `en_US-amy-medium` - Female, clear
- `en_GB-alan-medium` - Male British

**Other Languages:**
- German: `de_DE-thorsten-medium`
- French: `fr_FR-siwis-medium`
- Spanish: `es_ES-sharvard-medium`
- Italian: `it_IT-riccardo-medium`

See [Piper Voice Samples](https://rhasspy.github.io/piper-samples/) for the complete list.

### Voice Storage

Voice models are automatically downloaded on first run. Enable persistent storage to avoid re-downloading:

```yaml
persistence:
  enabled: true
  size: 2Gi  # Adjust based on voice size
```

## Advanced Configuration

### Adjusting Speech Speed

Control speaking rate with `lengthScale`:

```yaml
lengthScale: 0.8  # 20% faster
# lengthScale: 1.0  # Normal speed (default)
# lengthScale: 1.2  # 20% slower
```

### Multi-Speaker Voices

Some voices support multiple speakers:

```yaml
voice: en_US-libritts-high
speaker: "p225"  # Female speaker
```

### Resource Limits

Set appropriate resource limits:

```yaml
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 512Mi
```

### Service Discovery

Enable zeroconf/mDNS for automatic discovery:

```yaml
zeroconf: true
```

## Troubleshooting

### View Logs

```bash
kubectl logs -l app.kubernetes.io/name=wyoming-piper
```

### Check Service Status

```bash
kubectl get pods -l app.kubernetes.io/name=wyoming-piper
kubectl get svc -l app.kubernetes.io/name=wyoming-piper
```

### Voice Models Not Persisting

Ensure persistence is enabled and PVC is bound:

```bash
kubectl get pvc
```

### Port Forward for Testing

```bash
kubectl port-forward svc/piper-wyoming-piper 10200:10200
```

Then test with Wyoming client:

```bash
pip install wyoming
echo "Hello from Piper" | wyoming-client --uri tcp://localhost:10200 --type tts
```

### Audio Quality Issues

Adjust voice parameters for different characteristics:

```yaml
# More consistent speech
noiseScale: 0.5

# More natural/variable speech
noiseScale: 0.8

# Slower, clearer speech
lengthScale: 1.2
```

## Upgrading

```bash
helm upgrade piper oci://ghcr.io/mikesmitty/charts/wyoming-piper
```

To change the voice:

```bash
helm upgrade piper oci://ghcr.io/mikesmitty/charts/wyoming-piper \
  --set voice=en_US-lessac-high \
  --reuse-values
```

## Uninstalling

```bash
helm uninstall piper

# Optionally delete the PVC
kubectl delete pvc piper-wyoming-piper-data
```

## References

- [Wyoming Piper](https://github.com/rhasspy/wyoming-piper)
- [Piper TTS](https://github.com/rhasspy/piper)
- [Wyoming Protocol](https://github.com/rhasspy/wyoming)
- [Piper Voice Samples](https://rhasspy.github.io/piper-samples/)
- [Home Assistant Wyoming Integration](https://www.home-assistant.io/integrations/wyoming/)
