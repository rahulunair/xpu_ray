FROM intel/intel-extension-for-pytorch:2.3.110-xpu-pip-base

RUN apt-get update && apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    "ray[serve]" \
    "fastapi" \
    "diffusers" \
    "transformers" \
    "accelerate" \
    "Pillow" \
    "sentencepiece"

COPY sd.py /app/sd.py
COPY serve.py /app/serve.py
COPY start_serving.sh /app/

WORKDIR /app
ENTRYPOINT ["bash", "start_serving.sh"]
