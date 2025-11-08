# Ollama Intel GPU Helm Chart

[Ollama](https://ollama.ai/) with Intel GPU support and [Open WebUI](https://github.com/open-webui/open-webui) for running large language models on Kubernetes.

## Features

- Ollama server with Vulkan GPU support for Intel GPUs
- Open WebUI for easy model interaction
- Persistent storage for models and WebUI data
- Optional Ingress for external access
- Secure by default with non-root containers

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- (Optional) Intel GPU with drivers installed
- (Optional) [Intel GPU Device Plugin](https://github.com/intel/intel-device-plugins-for-kubernetes)

## Quick Start

### Basic Installation (CPU Only)

```bash
helm install ollama oci://ghcr.io/mikesmitty/charts/ollama-intel
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
ollama:
  resources:
    limits:
      gpu.intel.com/i915: 1  # For older Intel GPUs (Gen 9-12)
      # gpu.intel.com/xe: 1  # For newer Intel GPUs (Arc, Flex, Max)
    requests:
      gpu.intel.com/i915: 1

  nodeSelector:
    intel.feature.node.kubernetes.io/gpu: "true"
```

Install the chart:

```bash
helm install ollama oci://ghcr.io/mikesmitty/charts/ollama-intel -f values.yaml
```

### With Ingress

```yaml
webui:
  ingress:
    enabled: true
    className: nginx
    hosts:
      - host: ollama.example.com
        paths:
          - path: /
            pathType: Prefix
    tls:
      - secretName: ollama-tls
        hosts:
          - ollama.example.com
```

## Accessing Open WebUI

### Via Port Forward

```bash
kubectl port-forward service/ollama-webui 3000:8080
```

Then open http://localhost:3000 in your browser.

### Via Ingress

If you enabled Ingress, access the WebUI at your configured hostname.

## Using Ollama

### Pull a Model

```bash
kubectl exec -it deployment/ollama-ollama -- ollama pull llama3.2
```

### List Models

```bash
kubectl exec -it deployment/ollama-ollama -- ollama list
```

### Run a Model

```bash
kubectl exec -it deployment/ollama-ollama -- ollama run llama3.2 "Hello!"
```

## Configuration

### Key Parameters

#### Ollama Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ollama.replicaCount` | Number of Ollama replicas | `1` |
| `ollama.image.repository` | Ollama image | `ghcr.io/mikesmitty/ollama-vulkan` |
| `ollama.image.tag` | Image tag (empty = use appVersion) | `""` |
| `ollama.service.port` | Ollama service port | `11434` |
| `ollama.env.OLLAMA_KEEP_ALIVE` | Keep-alive duration | `"-1"` |
| `ollama.persistence.enabled` | Enable persistent storage | `true` |
| `ollama.persistence.size` | Storage size | `50Gi` |
| `ollama.resources` | CPU/Memory/GPU limits | `{}` |

#### WebUI Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `webui.enabled` | Enable Open WebUI | `true` |
| `webui.replicaCount` | Number of WebUI replicas | `1` |
| `webui.image.tag` | WebUI image tag | `"0.6.34"` |
| `webui.service.port` | WebUI service port | `8080` |
| `webui.persistence.enabled` | Enable persistent storage | `true` |
| `webui.persistence.size` | Storage size | `2Gi` |
| `webui.ingress.enabled` | Enable Ingress | `false` |

### Intel GPU Selection

Choose the appropriate GPU resource based on your hardware:

```yaml
# For older Intel GPUs (Gen 9-12, UHD Graphics)
ollama:
  resources:
    limits:
      gpu.intel.com/i915: 1
    requests:
      gpu.intel.com/i915: 1

# For newer Intel GPUs (Arc, Flex, Max)
ollama:
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

### Storage Configuration

Adjust storage sizes based on your model requirements:

```yaml
ollama:
  persistence:
    enabled: true
    size: 100Gi  # Large models need more space

webui:
  persistence:
    enabled: true
    size: 5Gi  # For WebUI data
```

## Advanced Configuration

### Resource Limits

Set appropriate CPU and memory limits:

```yaml
ollama:
  resources:
    limits:
      cpu: 4000m
      memory: 16Gi
      gpu.intel.com/i915: 1
    requests:
      cpu: 2000m
      memory: 8Gi
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

## Troubleshooting

### View Logs

```bash
# Ollama logs
kubectl logs -l app.kubernetes.io/component=ollama

# WebUI logs
kubectl logs -l app.kubernetes.io/component=webui
```

### Check Service Status

```bash
kubectl get pods -l app.kubernetes.io/name=ollama-intel
kubectl get svc
```

### GPU Not Detected

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

### Models Not Persisting

Verify PVC is bound:

```bash
kubectl get pvc
```

### WebUI Cannot Connect to Ollama

Check Ollama service:

```bash
kubectl get svc ollama-ollama
kubectl logs deployment/ollama-ollama
```

Verify WebUI environment:

```bash
kubectl exec deployment/ollama-webui -- env | grep OLLAMA_BASE_URL
```

## Upgrading

```bash
helm upgrade ollama oci://ghcr.io/mikesmitty/charts/ollama-intel
```

## Uninstalling

```bash
helm uninstall ollama

# Optionally delete PVCs
kubectl delete pvc -l app.kubernetes.io/instance=ollama
```

## Common Model Recommendations

### Small Models (Good for Intel GPUs)
- `llama3.2:3b` - Fast, efficient
- `phi4:latest` - Microsoft's compact model
- `qwen2.5:7b` - Alibaba's multilingual model

### Medium Models
- `llama3.1:8b` - General purpose
- `mistral:7b` - High quality responses

### Large Models (Requires significant resources)
- `llama3.1:70b` - Best quality
- `mixtral:8x7b` - Mixture of experts

Pull a model via kubectl:

```bash
kubectl exec -it deployment/ollama-ollama -- ollama pull llama3.2:3b
```

## References

- [Ollama](https://ollama.ai/)
- [Open WebUI](https://github.com/open-webui/open-webui)
- [Intel GPU Device Plugin](https://github.com/intel/intel-device-plugins-for-kubernetes)
- [Ollama Models](https://ollama.ai/library)
