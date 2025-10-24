# Kokoro Wyoming Helm Chart

This Helm chart deploys [Kokoro Wyoming](https://github.com/nordwestt/kokoro-wyoming) text-to-speech service on Kubernetes. Kokoro Wyoming provides high-quality neural TTS using the Kokoro ONNX model with Wyoming protocol support for Home Assistant voice assistants.

## Overview

This chart is optimized for **Home Assistant voice assistant** deployments with a focus on:
- **High-quality voices** - Neural TTS with natural-sounding speech
- **Intel GPU acceleration** - Efficient inference with OpenVINO
- **Easy integration** - Direct Wyoming protocol support for Home Assistant

The chart deploys:
- **Kokoro Wyoming** (`ghcr.io/mikesmitty/kokoro-wyoming`) - Kokoro TTS with Wyoming protocol support
- **Persistent Storage** - Optional PVC for caching models (recommended)
- **Health Checks** - Liveness and readiness probes for reliability

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Persistent storage (recommended for model caching)
- (Optional) Intel GPU with device plugin for GPU acceleration

## Installation

### Install from OCI Registry (Recommended)

Install the latest release from GitHub Container Registry:

```bash
helm install kokoro oci://ghcr.io/mikesmitty/kokoro-wyoming
```

Install a specific version:

```bash
helm install kokoro oci://ghcr.io/mikesmitty/kokoro-wyoming --version 0.5.0
```

### Install from Source

For development or local testing:

```bash
git clone https://github.com/mikesmitty/wyoming-helm.git
cd wyoming-helm
helm install kokoro ./charts/kokoro-wyoming
```

### Custom Configuration

Create a values file for your environment (e.g., `production.yaml`, `homeassistant.yaml`):

```yaml
# Enable Intel GPU acceleration
onnxProvider: OpenVINOExecutionProvider

# Enable persistent storage (recommended)
persistence:
  enabled: true
  size: 2Gi

# Resource limits for Intel GPU
resources:
  limits:
    cpu: 1000m
    memory: 2Gi
    gpu.intel.com/i915: 1
  requests:
    cpu: 250m
    memory: 1Gi
    gpu.intel.com/i915: 1

# Target Intel GPU nodes
nodeSelector:
  intel.feature.node.kubernetes.io/gpu: "true"
```

Install with custom values from OCI:

```bash
helm install kokoro oci://ghcr.io/mikesmitty/kokoro-wyoming -f production.yaml
```

Or from source:

```bash
helm install kokoro ./charts/kokoro-wyoming -f production.yaml
```

## Configuration

The following table lists the configurable parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Kokoro Wyoming image repository | `ghcr.io/mikesmitty/kokoro-wyoming` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `10210` |
| `onnxProvider` | ONNX execution provider | `OpenVINOExecutionProvider` |
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

## ONNX Execution Providers

Kokoro Wyoming supports different ONNX execution providers for optimization:

### OpenVINOExecutionProvider (Recommended for Intel Hardware)
- **Best for**: Intel CPUs and Intel GPUs
- **Performance**: Excellent with Intel GPU acceleration
- **Setup**: Set `onnxProvider: OpenVINOExecutionProvider`
- **Requirements**: Intel GPU device plugin if using GPU

```yaml
onnxProvider: OpenVINOExecutionProvider

resources:
  limits:
    gpu.intel.com/i915: 1
  requests:
    gpu.intel.com/i915: 1

nodeSelector:
  intel.feature.node.kubernetes.io/gpu: "true"
```

### CPUExecutionProvider
- **Best for**: General CPU inference without GPU
- **Performance**: Good for moderate TTS workloads
- **Setup**: Set `onnxProvider: CPUExecutionProvider`

```yaml
onnxProvider: CPUExecutionProvider

resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi
```

### CUDAExecutionProvider
- **Best for**: NVIDIA GPU acceleration
- **Performance**: Excellent with CUDA GPUs
- **Setup**: Set `onnxProvider: CUDAExecutionProvider`
- **Requirements**: NVIDIA GPU device plugin

```yaml
onnxProvider: CUDAExecutionProvider

resources:
  limits:
    nvidia.com/gpu: 1
  requests:
    nvidia.com/gpu: 1
```

## Available Voices

Voices are selected in Home Assistant when configuring the TTS provider. Available voices are read directly from the Kokoro model.

For a complete list of available voices, see:
- [Kokoro ONNX Voices](https://github.com/thewh1teagle/kokoro-onnx)

## Usage

### Accessing the Wyoming Service

After installation, get connection details:

```bash
helm status kokoro
```

For ClusterIP service (default), port-forward to access locally:

```bash
kubectl port-forward svc/kokoro-kokoro-wyoming 10210:10210
```

Then connect to `tcp://localhost:10210`

### Using with Home Assistant

Add to your Home Assistant `configuration.yaml`:

```yaml
wyoming:
  - platform: tts
    host: kokoro-kokoro-wyoming.default.svc.cluster.local
    port: 10210
```

Or if exposed externally via LoadBalancer:

```yaml
wyoming:
  - platform: tts
    host: <EXTERNAL_IP>
    port: 10210
```

## Advanced Configuration

### Optimizing for Intel GPU

For best performance with Intel GPUs:

```yaml
# Use OpenVINO execution provider
onnxProvider: OpenVINOExecutionProvider

# Request Intel GPU resources
resources:
  limits:
    cpu: 1000m
    memory: 2Gi
    gpu.intel.com/i915: 1
  requests:
    cpu: 250m
    memory: 1Gi
    gpu.intel.com/i915: 1

# Target nodes with Intel GPUs
nodeSelector:
  intel.feature.node.kubernetes.io/gpu: "true"

# Cache models for quick startup
persistence:
  enabled: true
  size: 2Gi
```

### Debug Logging

Enable debug mode for troubleshooting:

```yaml
debug: true
```

### Complete Home Assistant TTS Example

Full configuration optimized for Home Assistant with Intel GPU:

```yaml
# Intel GPU acceleration
onnxProvider: OpenVINOExecutionProvider

# Enable model caching
persistence:
  enabled: true
  size: 2Gi

# Intel GPU resources
resources:
  limits:
    cpu: 1000m
    memory: 2Gi
    gpu.intel.com/i915: 1
  requests:
    cpu: 250m
    memory: 1Gi
    gpu.intel.com/i915: 1

# Target Intel GPU nodes
nodeSelector:
  intel.feature.node.kubernetes.io/gpu: "true"

# Internal service (accessed from Home Assistant)
service:
  type: ClusterIP
  port: 10210
```

## Troubleshooting

### View logs

```bash
kubectl logs -l app.kubernetes.io/name=kokoro-wyoming
```

### Model cache issues

If models are being re-downloaded on every restart:
- Ensure `persistence.enabled: true` in your values
- Check PVC is bound: `kubectl get pvc`

### Service not responding

Check pod status:
```bash
kubectl get pods -l app.kubernetes.io/name=kokoro-wyoming
kubectl describe pod <pod-name>
```

Check if the readiness probe is passing:
```bash
kubectl get pods -l app.kubernetes.io/name=kokoro-wyoming -o wide
```

### Intel GPU not detected

Ensure the Intel GPU device plugin is installed:
```bash
kubectl get nodes -o json | jq '.items[].status.allocatable | select(."gpu.intel.com/i915" != null)'
```

## Uninstallation

To uninstall/delete the deployment:

```bash
helm uninstall kokoro
```

To also delete the PVC:

```bash
kubectl delete pvc kokoro-kokoro-wyoming-cache
```

## Upgrading

### To a newer chart version

From OCI registry:

```bash
helm upgrade kokoro oci://ghcr.io/mikesmitty/kokoro-wyoming --version 0.5.0
```

From source:

```bash
helm upgrade kokoro ./charts/kokoro-wyoming
```

## References

- [Kokoro Wyoming](https://github.com/nordwestt/kokoro-wyoming)
- [Kokoro ONNX](https://github.com/thewh1teagle/kokoro-onnx)
- [Wyoming Protocol](https://github.com/rhasspy/wyoming)
- [Home Assistant Wyoming Integration](https://www.home-assistant.io/integrations/wyoming/)
- [Intel GPU Device Plugin](https://github.com/intel/intel-device-plugins-for-kubernetes)
