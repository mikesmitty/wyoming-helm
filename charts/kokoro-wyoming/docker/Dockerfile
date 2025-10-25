FROM ghcr.io/astral-sh/uv:0.9.5-python3.12-trixie-slim

# Version comment to trigger a rebuild when updated
# x-release-please-start-version
# version 0.5.2
# x-release-please-end

ENV PYTHONPATH=/app

RUN useradd -m kokoro

WORKDIR /app/src

# Download required model files
RUN mkdir -p /app/src
ADD --checksum=sha256:7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5 https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx /app/src/kokoro-v1.0.onnx
ADD --checksum=sha256:bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin /app/src/voices-v1.0.bin

# Download main.py from nordwestt/kokoro-wyoming
ADD --checksum=sha256:2f4ac09d3355d3aeaecd3c19b106eef834a46b36d3c2189827fa82653deea1bd https://github.com/nordwestt/kokoro-wyoming/raw/d0ad1a99e7bf8cd9bf09ade2dc44cd4c55e6d43f/src/main.py /app/src/main.py

# Install required packages
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Change ownership to non-root user
RUN chown -R kokoro:kokoro /app

# Switch to non-root user
USER kokoro

ENTRYPOINT ["/usr/local/bin/python3", "main.py"]