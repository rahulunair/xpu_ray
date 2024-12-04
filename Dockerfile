FROM intel/intel-extension-for-pytorch:2.3.110-xpu-pip-base

RUN apt-get update && apt-get install -y \
    python3-pip \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    "ray[serve]>=2.40.0" \
    "fastapi>=0.115.6" \
    "diffusers==0.31.0" \
    "transformers==4.46.3" \
    "accelerate==1.1.1" \
    "Pillow==10.4.0" \
    "sentencepiece==0.2.0" \
    "psutil==6.0.0"

RUN pip install --no-cache-dir --pre pytorch-triton-xpu==3.0.0+1b2f15840e \
    --index-url https://download.pytorch.org/whl/nightly/xpu || echo "Triton installation failed, continuing without it"

COPY sd.py /app/sd.py
COPY serve.py /app/serve.py
COPY serve_config.yaml /app/serve_config.yaml
COPY start_serving.sh /app/start_serving.sh

WORKDIR /app

RUN chmod +x /app/start_serving.sh

ENTRYPOINT ["bash", "start_serving.sh"]
