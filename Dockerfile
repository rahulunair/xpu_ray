FROM intel/intel-extension-for-pytorch:2.3.110-xpu-pip-base

RUN apt-get update && apt-get install -y \
    python3-pip \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    "ray[serve]==2.9.0" \
    "fastapi>=0.68.0,<0.69.0" \
    "diffusers" \
    "transformers" \
    "accelerate" \
    "Pillow" \
    "sentencepiece" \
    "psutil"

RUN pip install --no-cache-dir --pre pytorch-triton-xpu==3.0.0+1b2f15840e \
    --index-url https://download.pytorch.org/whl/nightly/xpu || echo "Triton installation failed, continuing without it"

COPY sd.py /app/sd.py
COPY serve.py /app/serve.py
COPY start_serving.sh /app/

WORKDIR /app

RUN chmod +x /app/start_serving.sh

EXPOSE 6379 8265 9002

ENTRYPOINT ["bash", "start_serving.sh"]
