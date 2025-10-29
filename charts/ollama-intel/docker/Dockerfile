FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN useradd -m -d /app ollama

WORKDIR /app

# Version comment to trigger a rebuild when updated
# x-release-please-start-version
# version 0.1.3
# x-release-please-end

# Base packages
RUN apt update && \
    apt upgrade -y && \
    apt install --no-install-recommends -q -y \
    software-properties-common \
    ca-certificates \
    curl \
    ocl-icd-libopencl1

RUN add-apt-repository -y ppa:kobuk-team/intel-graphics && \
    apt-get install -y libze-intel-gpu1 libze1 intel-ocloc intel-opencl-icd clinfo intel-gsc intel-media-va-driver-non-free \
    libigdgmm12 libmfx1 libmfx-gen1 libvpl2 libvpl-tools libva-glx2 va-driver-all vainfo

# Install Ollama Portable Zip
ARG IPEXLLM_RELEASE_REPO=ipex-llm/ipex-llm
ARG IPEXLLM_RELEASE_VERSION=v2.2.0
ARG IPEXLLM_PORTABLE_ZIP_FILENAME=ollama-ipex-llm-2.2.0-ubuntu.tgz
RUN curl -LO https://github.com/${IPEXLLM_RELEASE_REPO}/releases/download/${IPEXLLM_RELEASE_VERSION}/${IPEXLLM_PORTABLE_ZIP_FILENAME} && \
    tar xvf ${IPEXLLM_PORTABLE_ZIP_FILENAME} --strip-components=1 -C ./ && \
    rm ${IPEXLLM_PORTABLE_ZIP_FILENAME}

# OLLAMA_HOST is hardcoded to localhost in the startup script in 2.3.0-nightly
RUN sed -i "s/export OLLAMA_HOST='127.0.0.1:11434'/export OLLAMA_HOST='0.0.0.0:11434'/" start-ollama.sh
# Works around an intermittent model loading failure with the Arc B580
RUN sed -i "s/export OLLAMA_KEEP_ALIVE=10m/export OLLAMA_KEEP_ALIVE=-1/" start-ollama.sh

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN chown -R ollama:ollama /app

USER ollama

ENTRYPOINT ["/bin/bash", "/app/start-ollama.sh"]