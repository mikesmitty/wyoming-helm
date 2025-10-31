# Ollama Intel GPU Helm Chart

This Helm chart deploys [Ollama](https://ollama.ai/) with Intel GPU support using Vulkan and [Open WebUI](https://github.com/open-webui/open-webui) on Kubernetes.

## Features

- Ollama server with Vulkan GPU support
- Optional llama.cpp server with Intel GPU support (alternative to Ollama)
- Open WebUI for easy interaction with Ollama models
- Persistent storage for models and WebUI data (separate storage for llama.cpp models)
- Intel GPU support via device plugin (no privileged containers required)
- Configurable resource limits and requests
- Optional Ingress support for external access
- Health checks (liveness and readiness probes)
- Secure by default with non-root containers

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Intel GPU available on Kubernetes nodes
- Intel GPU drivers installed on nodes
- [Intel GPU Device Plugin](https://github.com/intel/intel-device-plugins-for-kubernetes) installed on the cluster
- [Node Feature Discovery (NFD)](https://kubernetes-sigs.github.io/node-feature-discovery/) operator (optional, for automatic node labeling)
- PersistentVolume provisioner (if using persistent storage)

## Intel GPU Setup

### Install Intel GPU Device Plugin

The Intel GPU Device Plugin exposes GPU devices to Kubernetes without requiring privileged containers:

```bash
# Install using Kustomize
kubectl apply -k https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/gpu_plugin/overlays/nfd_labeled_nodes
```

Or with Helm:

```bash
helm repo add intel https://intel.github.io/helm-charts
helm install intel-gpu-plugin intel/intel-device-plugins-gpu
```

### Install Node Feature Discovery (Optional)

NFD automatically labels nodes with Intel GPU capabilities:

```bash
helm repo add nfd https://kubernetes-sigs.github.io/node-feature-discovery/charts
helm install nfd nfd/node-feature-discovery
```

After installation, verify GPU resources are available:

```bash
# Check for GPU resources on nodes
kubectl get nodes -o json | jq '.items[].status.allocatable | select(."gpu.intel.com/i915" != null or ."gpu.intel.com/xe" != null)'
```

## Docker Image

The chart uses a pre-built Docker image from GitHub Container Registry:
- `ghcr.io/mikesmitty/ollama-vulkan`

The image is automatically built from the upstream [ollama](https://github.com/ollama/ollama) repository via GitHub Actions (see [.github/workflows/build-ollama-upstream.yaml](.github/workflows/build-ollama-upstream.yaml)). It uses the official Ollama Dockerfile with Vulkan GPU support.

### Image Versioning

By default, the chart uses the `appVersion` from [Chart.yaml](charts/ollama-intel/Chart.yaml) as the image tag.

The appVersion is automatically kept up to date with the latest Ollama releases via Renovate Bot.

You can override the tag in `values.yaml` if needed:
```yaml
ollama:
  image:
    tag: "0.12.7"  # Use a specific version
```

## Installation

### Add the repository (if published to a Helm repo)

```bash
helm repo add wyoming-helm https://your-repo-url
helm repo update
```

### Install the chart

```bash
# Install with default values
helm install my-ollama wyoming-helm/ollama-intel

# Install with custom values
helm install my-ollama wyoming-helm/ollama-intel -f custom-values.yaml

# Install from local chart directory
helm install my-ollama ./charts/ollama-intel
```

## Configuration

The following table lists the configurable parameters and their default values.

### Ollama Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ollama.replicaCount` | Number of Ollama replicas | `1` |
| `ollama.image.repository` | Ollama image repository | `ghcr.io/mikesmitty/ollama-vulkan` |
| `ollama.image.tag` | Ollama image tag (empty = use appVersion) | `""` |
| `ollama.image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `ollama.service.type` | Kubernetes service type | `ClusterIP` |
| `ollama.service.port` | Ollama service port | `11434` |
| `ollama.env.OLLAMA_HOST` | Ollama bind address | `"0.0.0.0:11434"` |
| `ollama.env.OLLAMA_KEEP_ALIVE` | Keep-alive duration | `"-1"` |
| `ollama.persistence.enabled` | Enable persistent storage | `true` |
| `ollama.persistence.size` | Storage size | `50Gi` |
| `ollama.persistence.mountPath` | Mount path for models | `/home/ubuntu/.ollama` |
| `ollama.persistence.storageClass` | Storage class | `""` |
| `ollama.persistence.accessMode` | Access mode | `ReadWriteOnce` |
| `ollama.resources` | CPU/Memory/GPU resource requests/limits | `{}` |
| `ollama.securityContext` | Container security context | See values.yaml |

### WebUI Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `webui.enabled` | Enable Open WebUI | `true` |
| `webui.replicaCount` | Number of WebUI replicas | `1` |
| `webui.image.repository` | WebUI image repository | `ghcr.io/open-webui/open-webui` |
| `webui.image.tag` | WebUI image tag | `"0.6.34"` |
| `webui.service.type` | Kubernetes service type | `ClusterIP` |
| `webui.service.port` | WebUI service port | `8080` |
| `webui.service.externalPort` | External port for port-forward | `3000` |
| `webui.persistence.enabled` | Enable persistent storage | `true` |
| `webui.persistence.size` | Storage size | `2Gi` |
| `webui.ingress.enabled` | Enable Ingress | `false` |
| `webui.ingress.className` | Ingress class name | `""` |
| `webui.ingress.hosts` | Ingress hosts | `[{host: ollama-webui.local, paths: [{path: /, pathType: Prefix}]}]` |

### Llama.cpp Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `llamacpp.enabled` | Enable llama.cpp server (alternative to Ollama) | `false` |
| `llamacpp.replicaCount` | Number of llama.cpp replicas | `1` |
| `llamacpp.image.repository` | Llama.cpp image repository | `ghcr.io/mikesmitty/llama-cpp-intel` |
| `llamacpp.image.tag` | Llama.cpp image tag | `"server-intel-b6869"` |
| `llamacpp.image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `llamacpp.service.type` | Kubernetes service type | `ClusterIP` |
| `llamacpp.service.port` | Llama.cpp service port | `8080` |
| `llamacpp.model.ollama` | Ollama model to download (e.g., "llama3.2:3b") | `""` |
| `llamacpp.model.huggingface` | HuggingFace model (e.g., "bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0") | `""` |
| `llamacpp.model.path` | Local model path (relative to mountPath) | `""` |
| `llamacpp.model.pullPolicy` | Model pull policy for Ollama models (Always/IfNotPresent/Never) | `IfNotPresent` |
| `llamacpp.args.ctxSize` | Context size (token limit) | `2048` |
| `llamacpp.args.nGpuLayers` | Number of GPU layers to offload (-1 for all) | `40` |
| `llamacpp.args.extra` | Additional command-line arguments | `[]` |
| `llamacpp.env.ONEAPI_DEVICE_SELECTOR` | OneAPI device selector | `"level_zero:0"` |
| `llamacpp.persistence.enabled` | Enable persistent storage | `true` |
| `llamacpp.persistence.size` | Storage size | `50Gi` |
| `llamacpp.persistence.storageClass` | Storage class | `""` |
| `llamacpp.persistence.accessMode` | Access mode | `ReadWriteOnce` |
| `llamacpp.persistence.mountPath` | Mount path for models | `/models` |
| `llamacpp.resources` | CPU/Memory/GPU resource requests/limits | `{}` |
| `llamacpp.securityContext` | Container security context | See values.yaml |

### Common Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `nodeSelector` | Node labels for pod assignment | `{}` |
| `tolerations` | Tolerations for pod assignment | `[]` |
| `affinity` | Affinity rules for pod assignment | `{}` |
| `imagePullSecrets` | Image pull secrets | `[]` |

## Examples

### Basic Installation

```bash
helm install my-ollama ./charts/ollama-intel
```

### With Intel GPU Acceleration

```yaml
# values.yaml
ollama:
  resources:
    limits:
      cpu: 4000m
      memory: 16Gi
      gpu.intel.com/i915: 1  # For older Intel GPUs (Gen 9-12)
      # gpu.intel.com/xe: 1  # For newer Intel Xe GPUs (Arc, Flex, Max)
    requests:
      cpu: 2000m
      memory: 8Gi
      gpu.intel.com/i915: 1
      # gpu.intel.com/xe: 1

nodeSelector:
  intel.feature.node.kubernetes.io/gpu: "true"
```

```bash
helm install my-ollama ./charts/ollama-intel -f values.yaml
```

### With Ingress Enabled

```yaml
# values.yaml
webui:
  ingress:
    enabled: true
    className: nginx
    annotations:
      cert-manager.io/cluster-issuer: letsencrypt-prod
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

### With Llama.cpp (Alternative to Ollama)

If you prefer to use llama.cpp instead of Ollama, you have three options for loading models:

#### Option 1: Download from Ollama Library

```yaml
# values.yaml
ollama:
  enabled: false  # Disable Ollama if you only want llama.cpp

llamacpp:
  enabled: true
  model:
    ollama: "llama3.2:3b"  # Download from Ollama library via ollama-downloader
    pullPolicy: IfNotPresent  # Options: Always, IfNotPresent, Never
  args:
    ctxSize: 2048
    nGpuLayers: 40
  resources:
    limits:
      cpu: 4000m
      memory: 16Gi
      gpu.intel.com/i915: 1  # For older Intel GPUs (Gen 9-12)
      # gpu.intel.com/xe: 1  # For newer Intel Xe GPUs (Arc, Flex, Max)
    requests:
      cpu: 2000m
      memory: 8Gi
      gpu.intel.com/i915: 1
      # gpu.intel.com/xe: 1

nodeSelector:
  intel.feature.node.kubernetes.io/gpu: "true"
```

#### Option 2: Download from HuggingFace

```yaml
# values.yaml
llamacpp:
  enabled: true
  model:
    huggingface: "bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0"
  args:
    ctxSize: 2048
    nGpuLayers: 40
```

#### Option 3: Use Pre-loaded Model

```yaml
# values.yaml
llamacpp:
  enabled: true
  model:
    path: "my-model.gguf"  # Relative to persistence.mountPath
  args:
    ctxSize: 2048
    nGpuLayers: 40
```

```bash
helm install my-ollama ./charts/ollama-intel -f values.yaml
```

**Model Loading Methods:**
1. **Ollama Models** (`model.ollama`): Downloaded directly from Ollama registry API using a minimal Python script in the init container
   - Stored in Ollama's standard directory structure at the PVC root (`manifests/`, `blobs/`)
   - Uses only Python stdlib (urllib, json) - no external dependencies
   - Supports pullPolicy: `Always`, `IfNotPresent` (default), `Never`

2. **HuggingFace Models** (`model.huggingface`): Downloaded directly by llama.cpp using the `--hf-repo` flag
   - Cached in `.cache/` subdirectory via `LLAMA_CACHE` environment variable
   - Format: `"repo/model:filename"` (e.g., `"bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0"`)

3. **Local Models** (`model.path`): Use a pre-loaded GGUF file from the persistent volume
   - Path is relative to the PVC root (e.g., `"my-model.gguf"`)

**Server Arguments:**
- `ctxSize`: Token context length (default: 2048)
- `nGpuLayers`: Number of layers to offload to GPU (default: 40, use -1 for all layers)
- `extra`: Additional command-line arguments as a list (e.g., `["--threads", "4"]`)

**Open WebUI Integration:**
- When llama.cpp is enabled, it's automatically added to Open WebUI as an OpenAI-compatible endpoint
- Models appear in the WebUI under the OpenAI models section
- No API key required (set to "none")

**About the Llama.cpp Image:**
- The chart uses a custom-built llama.cpp image with Intel SYCL support
- Built from the official [llama.cpp](https://github.com/ggml-org/llama.cpp) repository
- Compiled with `GGML_SYCL_F16=ON` for FP16 precision optimization on Intel GPUs
- Automatically built and updated via GitHub Actions (see [.github/workflows/build-llamacpp-intel.yaml](.github/workflows/build-llamacpp-intel.yaml))
- Tags follow the pattern: `server-intel` (latest) and `server-intel-{version}` (e.g., `server-intel-b6869`)

Note: Llama.cpp uses a separate persistent volume for models. While it supports the same GGUF model format as Ollama, the llama.cpp image is useful for running newer models that Ollama for Intel may not yet support due to slower update cycles.


## Usage

### Accessing Open WebUI

#### Port Forward (default)

```bash
kubectl port-forward service/my-ollama-webui 3000:8080
```

Then open http://localhost:3000 in your browser.

#### Ingress

If you enabled Ingress, access the WebUI at the configured hostname.

### Using Ollama CLI

Pull a model:

```bash
kubectl exec -it deployment/my-ollama-ollama -- ollama pull llama2
```

Run a model:

```bash
kubectl exec -it deployment/my-ollama-ollama -- ollama run llama2 "Hello, how are you?"
```

List models:

```bash
kubectl exec -it deployment/my-ollama-ollama -- ollama list
```

### API Access

Access the Ollama API from within the cluster:

```bash
curl http://my-ollama-ollama:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Why is the sky blue?"
}'
```

### Using Llama.cpp

If you enabled llama.cpp, you can access it via its service:

```bash
# Port forward to access llama.cpp locally
kubectl port-forward service/my-ollama-llamacpp 8080:8080

# Use the llama.cpp API
curl http://localhost:8080/v1/chat/completions -H "Content-Type: application/json" -d '{
  "model": "model-name",
  "messages": [{"role": "user", "content": "Hello!"}]
}'
```

Place your GGUF models in the persistent volume mounted at `/models`.

## Upgrading

```bash
helm upgrade my-ollama ./charts/ollama-intel -f values.yaml
```

## Uninstalling

```bash
helm uninstall my-ollama
```

Note: This will not delete the PersistentVolumeClaims. To delete them:

```bash
kubectl delete pvc -l app.kubernetes.io/instance=my-ollama
```

## Troubleshooting

### GPU Not Detected

Ensure:
1. Intel GPU Device Plugin is installed and running
2. Intel GPU drivers are installed on the nodes
3. GPU resources are requested in `ollama.resources` (`gpu.intel.com/i915` or `gpu.intel.com/xe`)
4. Node selector/affinity is correctly configured to schedule on GPU nodes (if using NFD)

Check GPU resources available on nodes:

```bash
kubectl get nodes -o json | jq '.items[].status.allocatable | select(."gpu.intel.com/i915" != null or ."gpu.intel.com/xe" != null)'
```

Verify GPU device plugin is running:

```bash
kubectl get pods -n kube-system | grep gpu-plugin
```

Check if your pod has GPU allocated:

```bash
kubectl describe pod -l app.kubernetes.io/component=ollama | grep -A 5 "Limits:"
```

### Models Not Persisting

Ensure `ollama.persistence.enabled` is set to `true` and that your cluster has a PersistentVolume provisioner configured.

### WebUI Cannot Connect to Ollama

Check that the Ollama service is running:

```bash
kubectl get svc my-ollama-ollama
kubectl logs deployment/my-ollama-ollama
```

Verify the WebUI environment variable:

```bash
kubectl exec deployment/my-ollama-webui -- env | grep OLLAMA_BASE_URL
```

## License

This Helm chart follows the same license as the underlying projects.
