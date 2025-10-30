#!/usr/bin/env python3
"""
Minimal Ollama model downloader for llama.cpp
Downloads models directly from Ollama registry API

Usage: python download-ollama-model.py <model:tag> <output_dir>
Example: python download-ollama-model.py llama3.2:3b /models
"""

import sys
import json
import urllib.request
import urllib.error
from pathlib import Path


REGISTRY_URL = "https://registry.ollama.ai/v2"


def download_file(url: str, output_path: Path, desc: str = ""):
    """Download a file with progress indication"""
    try:
        print(f"Downloading {desc}...")
        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(output_path, 'wb') as f:
                while chunk := response.read(8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='')

            if total_size > 0:
                print()  # New line after progress
        return True
    except urllib.error.HTTPError as e:
        print(f"\nError downloading {desc}: HTTP {e.code} - {e.reason}")
        return False
    except Exception as e:
        print(f"\nError downloading {desc}: {e}")
        return False


def get_manifest(model: str, tag: str) -> dict:
    """Fetch the model manifest from Ollama registry"""
    manifest_url = f"{REGISTRY_URL}/library/{model}/manifests/{tag}"
    print(f"Fetching manifest from {manifest_url}")

    try:
        with urllib.request.urlopen(manifest_url) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Error: Failed to fetch manifest (HTTP {e.code})")
        print(f"Model '{model}:{tag}' may not exist in the registry")
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching manifest: {e}")
        sys.exit(1)


def download_model(model_name: str, output_dir: str):
    """Download a model from Ollama registry"""

    # Parse model name and tag
    if ':' in model_name:
        model, tag = model_name.split(':', 1)
    else:
        model = model_name
        tag = 'latest'

    print(f"Downloading model: {model}:{tag}")

    # Setup directories
    base_dir = Path(output_dir)
    manifest_dir = base_dir / "manifests" / "registry.ollama.ai" / "library" / model
    blobs_dir = base_dir / "blobs"

    manifest_dir.mkdir(parents=True, exist_ok=True)
    blobs_dir.mkdir(parents=True, exist_ok=True)

    # Download manifest
    manifest = get_manifest(model, tag)

    # Save manifest
    manifest_file = manifest_dir / tag
    print(f"Saving manifest to {manifest_file}")
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    # Download blobs
    print(f"\nFound {len(manifest.get('layers', []))} layers to download")

    for idx, layer in enumerate(manifest.get('layers', []), 1):
        digest = layer.get('digest', '')
        if not digest.startswith('sha256:'):
            print(f"Skipping layer {idx}: invalid digest format")
            continue

        # Convert sha256:abc... to sha256-abc...
        blob_name = digest.replace(':', '-')
        blob_path = blobs_dir / blob_name

        # Skip if already exists
        if blob_path.exists():
            size = blob_path.stat().st_size
            print(f"Layer {idx}/{len(manifest['layers'])}: {blob_name} already exists ({size} bytes)")
            continue

        # Download blob
        blob_url = f"{REGISTRY_URL}/library/{model}/blobs/{digest}"
        media_type = layer.get('mediaType', 'unknown')
        size = layer.get('size', 0)

        desc = f"layer {idx}/{len(manifest['layers'])} ({media_type}, {size} bytes)"
        if not download_file(blob_url, blob_path, desc):
            print(f"Failed to download blob {blob_name}")
            sys.exit(1)

    print(f"\n✓ Model {model}:{tag} downloaded successfully!")
    print(f"  Manifest: {manifest_file}")
    print(f"  Blobs: {blobs_dir}")

    # Find and print the main model blob (usually the largest GGUF file)
    model_layers = [l for l in manifest.get('layers', [])
                   if l.get('mediaType') == 'application/vnd.ollama.image.model']

    if model_layers:
        main_blob = model_layers[0]['digest'].replace(':', '-')
        print(f"  Main model blob: {blobs_dir / main_blob}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python download-ollama-model.py <model:tag> <output_dir>")
        print("Example: python download-ollama-model.py llama3.2:3b /models")
        sys.exit(1)

    model_name = sys.argv[1]
    output_dir = sys.argv[2]

    download_model(model_name, output_dir)


# Note: When embedded in Helm templates, the if __name__ block is skipped
# and download_model() is called directly with template variables
if __name__ == '__main__' and len(sys.argv) > 1:
    main()
