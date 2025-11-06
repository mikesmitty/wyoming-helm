# Kokoro Wyoming Helm Chart

[Kokoro Wyoming](https://github.com/nordwestt/kokoro-wyoming) provides high-quality neural text-to-speech using the Kokoro ONNX model with Wyoming protocol support for Home Assistant voice assistants.

## Features

- High-quality neural TTS with natural-sounding speech
- Intel GPU acceleration with OpenVINO
- Wyoming protocol support for Home Assistant
- Built-in Kokoro v1.0 model in container image
- No persistent storage required (model included)

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- (Optional) Intel GPU with device plugin for GPU acceleration

## Quick Start

### Basic Installation (CPU Only)

```bash
helm install kokoro oci://ghcr.io/mikesmitty/kokoro-wyoming
```

### With Intel GPU Acceleration

First, ensure Intel GPU Device Plugin is installed:

```bash
# Using Kustomize
kubectl apply -k https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/gpu_plugin/overlays/nfd_labeled_nodes

# Or using Helm
helm repo add intel https://intel.github.io/helm-charts
helm install intel-gpu-plugin intel/intel-device-plugins-gpu
```

Create a `values.yaml` file:

```yaml
# Use OpenVINO for Intel GPU acceleration
onnxProvider: OpenVINOExecutionProvider

resources:
  limits:
    cpu: 1000m
    memory: 2Gi
    gpu.intel.com/i915: 1  # For older Intel GPUs (Gen 9-12)
    # gpu.intel.com/xe: 1  # For newer Intel GPUs (Arc, Flex, Max)
  requests:
    cpu: 250m
    memory: 1Gi
    gpu.intel.com/i915: 1

nodeSelector:
  intel.feature.node.kubernetes.io/gpu: "true"
```

Install the chart:

```bash
helm install kokoro oci://ghcr.io/mikesmitty/kokoro-wyoming -f values.yaml
```

## Using with Home Assistant

After installation, add to your Home Assistant `configuration.yaml`:

```yaml
wyoming:
  - platform: tts
    host: kokoro-kokoro-wyoming.default.svc.cluster.local
    port: 10210
```

**Note**: Replace `default` with your namespace if different, and `kokoro` with your release name if different.

Voices are selected in Home Assistant when configuring the TTS provider.

## Configuration

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Kokoro image | `ghcr.io/mikesmitty/kokoro-wyoming-tts` |
| `image.tag` | Image tag | `""` (uses appVersion) |
| `service.port` | Service port | `10210` |
| `onnxProvider` | ONNX execution provider | `OpenVINOExecutionProvider` |
| `debug` | Enable debug logging | `false` |
| `resources` | CPU/Memory/GPU limits | `{}` |

### ONNX Execution Providers

Choose the appropriate provider for your hardware:

#### OpenVINOExecutionProvider (Recommended for Intel)

Best for Intel CPUs and Intel GPUs:

```yaml
onnxProvider: OpenVINOExecutionProvider

# With Intel GPU
resources:
  limits:
    gpu.intel.com/i915: 1
  requests:
    gpu.intel.com/i915: 1

nodeSelector:
  intel.feature.node.kubernetes.io/gpu: "true"
```

#### CPUExecutionProvider

For general CPU inference without GPU:

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

#### CUDAExecutionProvider

For NVIDIA GPU acceleration:

```yaml
onnxProvider: CUDAExecutionProvider

resources:
  limits:
    nvidia.com/gpu: 1
  requests:
    nvidia.com/gpu: 1
```

### Intel GPU Selection

Choose the appropriate GPU resource based on your hardware:

```yaml
# For older Intel GPUs (Gen 9-12, UHD Graphics)
resources:
  limits:
    gpu.intel.com/i915: 1
  requests:
    gpu.intel.com/i915: 1

# For newer Intel GPUs (Arc, Flex, Max)
resources:
  limits:
    gpu.intel.com/xe: 1
  requests:
    gpu.intel.com/xe: 1
```

Verify GPU resources are available:

```bash
kubectl get nodes -o json | jq '.items[].status.allocatable | select(."gpu.intel.com/i915" != null or ."gpu.intel.com/xe" != null)'
```

## Available Voices

Voices are read directly from the Kokoro model and selected in Home Assistant. For a complete list of available voices, see:

- [Kokoro ONNX Voices](https://github.com/thewh1teagle/kokoro-onnx)

## Advanced Configuration

### Resource Limits

Set appropriate resource limits based on your workload:

```yaml
# For Intel GPU acceleration
resources:
  limits:
    cpu: 1000m
    memory: 2Gi
    gpu.intel.com/i915: 1
  requests:
    cpu: 250m
    memory: 1Gi
    gpu.intel.com/i915: 1
```

### Node Scheduling

Target specific nodes with Intel GPUs:

```yaml
nodeSelector:
  intel.feature.node.kubernetes.io/gpu: "true"

# Or use affinity for more control
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: intel.feature.node.kubernetes.io/gpu
          operator: In
          values:
          - "true"
```

### Debug Logging

Enable debug mode for troubleshooting:

```yaml
debug: true
```

## Troubleshooting

### View Logs

```bash
kubectl logs -l app.kubernetes.io/name=kokoro-wyoming
```

### Check Service Status

```bash
kubectl get pods -l app.kubernetes.io/name=kokoro-wyoming
kubectl get svc -l app.kubernetes.io/name=kokoro-wyoming
```

### Intel GPU Not Detected

Ensure:
1. Intel GPU Device Plugin is installed
2. Intel GPU drivers are installed on nodes
3. GPU resources are requested in values
4. Node selector matches GPU nodes

Check GPU availability:

```bash
# Check GPU plugin pods
kubectl get pods -n kube-system | grep gpu-plugin

# Check GPU resources on nodes
kubectl describe node <node-name> | grep -A 5 "Allocatable"
```

### Port Forward for Testing

```bash
kubectl port-forward svc/kokoro-kokoro-wyoming 10210:10210
```

Then test with Wyoming client:

```bash
pip install wyoming
echo "Hello from Kokoro" | wyoming-client --uri tcp://localhost:10210 --type tts
```

## Upgrading

```bash
helm upgrade kokoro oci://ghcr.io/mikesmitty/kokoro-wyoming
```

## Uninstalling

```bash
helm uninstall kokoro
```

**Note**: Kokoro does not use persistent storage since the model is included in the container image.

## References

- [Kokoro Wyoming](https://github.com/nordwestt/kokoro-wyoming)
- [Kokoro ONNX](https://github.com/thewh1teagle/kokoro-onnx)
- [Wyoming Protocol](https://github.com/rhasspy/wyoming)
- [Home Assistant Wyoming Integration](https://www.home-assistant.io/integrations/wyoming/)
- [Intel GPU Device Plugin](https://github.com/intel/intel-device-plugins-for-kubernetes)
