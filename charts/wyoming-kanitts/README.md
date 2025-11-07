# Wyoming KaniTTS Helm Chart

[KaniTTS](https://github.com/nineninesix-ai/kani-tts) is a fast, high-quality text-to-speech model that provides Wyoming protocol support for Home Assistant voice assistants. This chart deploys KaniTTS with Intel XPU (GPU) acceleration support via PyTorch.

## Features

- High-quality neural TTS with KaniTTS-370M or KaniTTS-450M models
- Intel GPU acceleration via PyTorch XPU backend
- NVIDIA GPU support (CUDA)
- CPU fallback support
- Wyoming protocol integration for Home Assistant
- Persistent model storage
- Configurable resource limits and GPU selection

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Persistent storage (recommended)
- For Intel GPU acceleration:
  - Intel GPU Device Plugin installed
  - PyTorch 2.5+ with XPU support in container
  - Intel GPU drivers on nodes
- For NVIDIA GPU: NVIDIA GPU Device Plugin

## Quick Start

### Basic Installation (CPU Only)

```bash
helm install kanitts oci://ghcr.io/mikesmitty/wyoming-kanitts
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
# Use Intel XPU device for GPU acceleration
device: "xpu"

# Intel XPU configuration
xpu:
  backend: "level_zero"
  deviceIndex: 0

# Select KaniTTS model
model:
  name: "nineninesix/kani-tts-370m"

# Resource allocation
resources:
  limits:
    cpu: 2000m
    memory: 4Gi
    gpu.intel.com/i915: 1  # For older Intel GPUs (Gen 9-12)
    # gpu.intel.com/xe: 1  # For newer Intel GPUs (Arc, Flex, Max)
  requests:
    cpu: 500m
    memory: 2Gi
    gpu.intel.com/i915: 1

# Schedule on Intel GPU nodes
nodeSelector:
  intel.feature.node.kubernetes.io/gpu: "true"
```

Install the chart:

```bash
helm install kanitts oci://ghcr.io/mikesmitty/wyoming-kanitts -f values.yaml
```

### With NVIDIA GPU

```yaml
# Use CUDA device for NVIDIA GPU acceleration
device: "cuda"

# Select KaniTTS model
model:
  name: "nineninesix/kani-tts-370m"

# Resource allocation
resources:
  limits:
    nvidia.com/gpu: 1
  requests:
    nvidia.com/gpu: 1
```

## Using with Home Assistant

After installation, add to your Home Assistant `configuration.yaml`:

```yaml
wyoming:
  - platform: tts
    host: kanitts-wyoming-kanitts.default.svc.cluster.local
    port: 10220
```

**Note**: Replace `default` with your namespace if different, and `kanitts` with your release name if different.

## Configuration

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | KaniTTS Wyoming image | `ghcr.io/mikesmitty/wyoming-kanitts` |
| `image.tag` | Image tag | `""` (uses appVersion) |
| `service.port` | Service port | `10220` |
| `device` | PyTorch device | `xpu` |
| `model.name` | KaniTTS model name | `nineninesix/kani-tts-370m` |
| `persistence.enabled` | Enable persistent storage | `true` |
| `persistence.size` | Storage size | `5Gi` |
| `resources` | CPU/Memory/GPU limits | `{}` |

### Model Selection

KaniTTS provides two model sizes:

#### KaniTTS-370M (Recommended)
- Faster inference
- Lower memory usage (~2GB)
- Good quality for voice assistants

```yaml
model:
  name: "nineninesix/kani-tts-370m"
```

#### KaniTTS-450M
- Higher quality
- More memory usage (~3GB)
- Slower inference

```yaml
model:
  name: "nineninesix/kani-tts-450m-0.1-pt"
```

### Device Selection

The chart supports three device types:

#### Intel XPU (Recommended for Intel GPUs)

```yaml
device: "xpu"

xpu:
  backend: "level_zero"  # Use Level Zero for best performance
  deviceIndex: 0         # First Intel GPU

resources:
  limits:
    gpu.intel.com/i915: 1  # For Gen 9-12 (UHD, Iris Xe integrated)
    # gpu.intel.com/xe: 1  # For Arc, Flex, Max (discrete/newer)
```

#### NVIDIA CUDA

```yaml
device: "cuda"

resources:
  limits:
    nvidia.com/gpu: 1
```

#### CPU (Fallback)

```yaml
device: "cpu"

resources:
  limits:
    cpu: 2000m
    memory: 4Gi
```

### Intel GPU Selection

Choose the appropriate GPU resource based on your hardware:

```yaml
# For older Intel integrated GPUs (Gen 9-12, UHD Graphics, Iris Xe)
resources:
  limits:
    gpu.intel.com/i915: 1
  requests:
    gpu.intel.com/i915: 1

# For newer Intel discrete GPUs (Arc A-Series, Flex, Max)
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

### Environment Variables

Additional environment variables can be configured:

```yaml
env:
  ONEAPI_DEVICE_SELECTOR: "level_zero:0"
  PYTORCH_ENABLE_XPU: "1"

extraEnv:
  - name: CUSTOM_VAR
    value: "custom_value"
```

### Wyoming Protocol Options

```yaml
wyoming:
  debug: false
  extraArgs:
    - "--log-format"
    - "json"
```

## Advanced Configuration

### Resource Limits

Set appropriate resource limits based on your model and workload:

```yaml
# For Intel GPU with KaniTTS-370M
resources:
  limits:
    cpu: 2000m
    memory: 4Gi
    gpu.intel.com/i915: 1
  requests:
    cpu: 500m
    memory: 2Gi
    gpu.intel.com/i915: 1

# For Intel GPU with KaniTTS-450M (more memory needed)
resources:
  limits:
    cpu: 2000m
    memory: 6Gi
    gpu.intel.com/xe: 1
  requests:
    cpu: 500m
    memory: 3Gi
    gpu.intel.com/xe: 1
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

### Persistent Storage

Model files are cached to avoid re-downloading:

```yaml
persistence:
  enabled: true
  storageClass: "fast-ssd"
  accessMode: ReadWriteOnce
  size: 5Gi
  # Or use existing claim
  existingClaim: "my-kanitts-storage"
```

### Debug Logging

Enable debug mode for troubleshooting:

```yaml
wyoming:
  debug: true
```

## Troubleshooting

### View Logs

```bash
kubectl logs -l app.kubernetes.io/name=wyoming-kanitts
```

### Check Service Status

```bash
kubectl get pods -l app.kubernetes.io/name=wyoming-kanitts
kubectl get svc -l app.kubernetes.io/name=wyoming-kanitts
```

### Intel GPU Not Detected

Ensure:
1. Intel GPU Device Plugin is installed
2. Intel GPU drivers are installed on nodes
3. GPU resources are requested in values
4. Node selector matches GPU nodes
5. PyTorch XPU is enabled in container

Check GPU availability:

```bash
# Check GPU plugin pods
kubectl get pods -n kube-system | grep gpu-plugin

# Check GPU resources on nodes
kubectl describe node <node-name> | grep -A 5 "Allocatable"

# Check pod events
kubectl describe pod -l app.kubernetes.io/name=wyoming-kanitts
```

### Model Download Issues

If models fail to download:

```bash
# Check pod logs for download progress
kubectl logs -l app.kubernetes.io/name=wyoming-kanitts -f

# Verify persistent volume is mounted
kubectl describe pod -l app.kubernetes.io/name=wyoming-kanitts | grep -A 5 "Mounts"

# Check Hugging Face access (if needed)
# Set HF_TOKEN in extraEnv for gated models
```

### Port Forward for Testing

```bash
kubectl port-forward svc/kanitts-wyoming-kanitts 10220:10220
```

Then test with Wyoming client:

```bash
pip install wyoming
echo "Hello from KaniTTS" | wyoming-client --uri tcp://localhost:10220 --type tts
```

### PyTorch XPU Issues

Check XPU device availability inside container:

```bash
kubectl exec -it <pod-name> -- python3 -c "import torch; print(torch.xpu.is_available()); print(torch.xpu.device_count())"
```

Expected output:
```
True
1
```

If `False`, check:
- Intel GPU drivers on host node
- GPU device plugin running
- GPU resource allocated to pod
- ONEAPI_DEVICE_SELECTOR environment variable

## Building the Container Image

The chart expects a container image that:
1. Contains PyTorch 2.5+ with XPU support
2. Has kani-tts Python package installed
3. Includes a Wyoming protocol wrapper
4. Supports Intel Extension for PyTorch (IPEX) if needed

Example Dockerfile structure:

```dockerfile
FROM intel/intel-optimized-pytorch:2.5.0-xpu

# Install KaniTTS and dependencies
RUN pip install kani-tts transformers==4.57.1 wyoming

# Add Wyoming wrapper script
COPY wyoming_kanitts.py /app/

ENTRYPOINT ["python3", "/app/wyoming_kanitts.py"]
```

## Upgrading

```bash
helm upgrade kanitts oci://ghcr.io/mikesmitty/wyoming-kanitts
```

## Uninstalling

```bash
helm uninstall kanitts
```

To also delete persistent data:

```bash
kubectl delete pvc kanitts-wyoming-kanitts-data
```

## Comparison with Other TTS Charts

| Feature | wyoming-kanitts | kokoro-wyoming | wyoming-piper |
|---------|----------------|----------------|---------------|
| Quality | High | High | Good |
| Speed | Fast | Fast | Very Fast |
| GPU Support | Intel XPU, CUDA | Intel OpenVINO | CUDA (optional) |
| Model Size | 370M-450M | 82M | Varies |
| Backend | PyTorch | ONNX | ONNX |
| Memory Usage | 2-4GB | 1-2GB | 512MB-1GB |

**When to use KaniTTS:**
- You want high-quality neural TTS
- You have Intel GPUs with XPU support
- You prefer PyTorch over ONNX
- You need CUDA support option

**When to use Kokoro:**
- You want production-ready ONNX inference
- You have older Intel GPUs (i915)
- You prioritize stability

**When to use Piper:**
- You need the fastest, lightest TTS
- CPU-only deployment
- Minimal resource usage

## References

- [KaniTTS](https://github.com/nineninesix-ai/kani-tts)
- [KaniTTS Models on Hugging Face](https://huggingface.co/nineninesix)
- [Wyoming Protocol](https://github.com/rhasspy/wyoming)
- [Home Assistant Wyoming Integration](https://www.home-assistant.io/integrations/wyoming/)
- [Intel GPU Device Plugin](https://github.com/intel/intel-device-plugins-for-kubernetes)
- [PyTorch Intel GPU Support](https://pytorch.org/blog/intel-gpu-support-pytorch-2-5/)

## License

See the KaniTTS project for licensing information.
