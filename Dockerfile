FROM nvidia/cuda:12.6.0-cudnn9-runtime-ubuntu22.04

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.10 python3-pip python3.10-dev \
    libgl1-mesa-glx libglib2.0-0 wget \
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3.10 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# ✅ cu126 — the only CUDA 12 index PaddlePaddle publishes
RUN pip install --no-cache-dir \
    paddlepaddle-gpu==3.0.0 \
    -i https://www.paddlepaddle.org.cn/packages/stable/cu126/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY handler.py processor.py ./

CMD ["python", "-u", "handler.py"]
