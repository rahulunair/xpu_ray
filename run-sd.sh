#!/bin/bash

# Create required directories
mkdir -p $HOME/.cache/huggingface
mkdir -p $HOME/stable-diffusion-models/{transformers,diffusers}

# Run the container
docker run \
  --rm \
  --name stable-diffusion-xpu-container \
  --privileged \
  --cap-add=sys_nice \
  --device=/dev/dri \
  --ipc=host \
  --network=host \
  --shm-size=2g \
  -v $HOME/.cache/huggingface:/root/.cache/huggingface \
  -v $HOME/stable-diffusion-models:/models \
  -e TRANSFORMERS_CACHE=/models/transformers \
  -e DIFFUSERS_CACHE=/models/diffusers \
  -e HF_HOME=/root/.cache/huggingface \
  stable-diffusion-xpu
