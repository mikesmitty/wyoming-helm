# Changelog

## [0.3.0](https://github.com/mikesmitty/wyoming-helm/compare/ollama-intel-v0.2.4...ollama-intel-v0.3.0) (2025-10-30)


### Features

* make nodeSelector and affinity adjustable per component ([bbd62a7](https://github.com/mikesmitty/wyoming-helm/commit/bbd62a71b04d009cb25ec1794f00eb28c315efb4))

## [0.2.4](https://github.com/mikesmitty/wyoming-helm/compare/ollama-intel-v0.2.3...ollama-intel-v0.2.4) (2025-10-30)


### Bug Fixes

* use recreate deployment strategy ([5de926c](https://github.com/mikesmitty/wyoming-helm/commit/5de926c27f7fd2b0f961bc9a3b4a9ce90df42ad2))

## [0.2.3](https://github.com/mikesmitty/wyoming-helm/compare/ollama-intel-v0.2.2...ollama-intel-v0.2.3) (2025-10-30)


### Bug Fixes

* disable liveness probe by default ([4cbb611](https://github.com/mikesmitty/wyoming-helm/commit/4cbb611695cc11b7ec8e4aeebe77ae28b9265cad))
* fix ollama downloader ([797118b](https://github.com/mikesmitty/wyoming-helm/commit/797118bc46c1d62a649da10ebf88136afa28350b))
* switch to existing container uid ([67b178d](https://github.com/mikesmitty/wyoming-helm/commit/67b178d431e4c7cff914b73547713cfc19cb7962))

## [0.2.2](https://github.com/mikesmitty/wyoming-helm/compare/ollama-intel-v0.2.1...ollama-intel-v0.2.2) (2025-10-30)


### Bug Fixes

* replace model downloader ([6a27f9f](https://github.com/mikesmitty/wyoming-helm/commit/6a27f9fcbd1e8eb4fd828b07be3dff726766c29c))

## [0.2.1](https://github.com/mikesmitty/wyoming-helm/compare/ollama-intel-v0.2.0...ollama-intel-v0.2.1) (2025-10-29)


### Bug Fixes

* add args for llama.cpp ([0199244](https://github.com/mikesmitty/wyoming-helm/commit/01992442d92ca5a6bacfb4e38b69ea37f3838e95))

## [0.2.0](https://github.com/mikesmitty/wyoming-helm/compare/ollama-intel-v0.1.4...ollama-intel-v0.2.0) (2025-10-29)


### Features

* add llama.cpp deployment ([a38c944](https://github.com/mikesmitty/wyoming-helm/commit/a38c944123c44c1742c8c0736c0ed9ba5e45c9ef))

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
