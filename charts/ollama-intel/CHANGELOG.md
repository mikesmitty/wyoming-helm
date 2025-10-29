# Changelog

## [0.1.4](https://github.com/mikesmitty/wyoming-helm/compare/ollama-intel-v0.1.3...ollama-intel-v0.1.4) (2025-10-29)


### Bug Fixes

* add ollama bind port config and timeout ([79d5a56](https://github.com/mikesmitty/wyoming-helm/commit/79d5a564d7232a28071219f4a546d932bfd2d1a4))

## [0.1.3](https://github.com/mikesmitty/wyoming-helm/compare/ollama-intel-v0.1.2...ollama-intel-v0.1.3) (2025-10-29)


### Bug Fixes

* disable liveness probe by default ([f0519e8](https://github.com/mikesmitty/wyoming-helm/commit/f0519e8c81d541655dd7e121afb98ccba5acc056))
* update fsGroup to match gid ([c44be9f](https://github.com/mikesmitty/wyoming-helm/commit/c44be9fb2179bbe116787db490362dc3267f1c61))

## [0.1.2](https://github.com/mikesmitty/wyoming-helm/compare/ollama-intel-v0.1.1...ollama-intel-v0.1.2) (2025-10-29)


### Bug Fixes

* specify open-webui version ([2f3748f](https://github.com/mikesmitty/wyoming-helm/commit/2f3748f4bdb4cfd2b693481a821cac421fcdc084))
* use ipex-llm version for ollama-intel-gpu tag ([cbed911](https://github.com/mikesmitty/wyoming-helm/commit/cbed9110a3de062ae8bc25108b1796cb2dd9d0e0))

## [0.1.1](https://github.com/mikesmitty/wyoming-helm/compare/ollama-intel-0.1.0...ollama-intel-v0.1.1) (2025-10-28)


### Bug Fixes

* update persistence path ([6991338](https://github.com/mikesmitty/wyoming-helm/commit/69913383ce78d7a225e34657a8dcdb8776bc642d))
* update user id ([6991338](https://github.com/mikesmitty/wyoming-helm/commit/69913383ce78d7a225e34657a8dcdb8776bc642d))

## 0.1.0 (2025-10-28)


### Features

* add ollama-intel helm chart ([fbb9713](https://github.com/mikesmitty/wyoming-helm/commit/fbb9713e642d4ee02932cdc8cf67eac0677fa932))

## 0.1.0 (TBD)

### Features

* Initial release of ollama-intel chart
* Ollama server optimized for Intel GPUs with IPEX-LLM
* Open WebUI integration for easy model interaction
* Intel GPU support via device plugin (no privileged containers)
* Persistent storage for models and WebUI data
* Configurable resource limits with GPU resource requests
* Optional Ingress support for external access
* Secure by default with non-root containers
