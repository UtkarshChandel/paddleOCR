FROM nvidia/cuda:12.6.2-cudnn-runtime-ubuntu22.04

WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive
ENV PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True

RUN apt-get update && apt-get install -y \
    python3.11 python3-pip python3.11-dev \
    libgl1-mesa-glx libglib2.0-0 git \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3.11 /usr/bin/python

# Install PaddlePaddle 3.3.1 from Baidu index (has fused_rms_norm_ext)
RUN pip install paddlepaddle-gpu==3.3.1 \
    -i https://www.paddlepaddle.org.cn/packages/stable/cu126/ \
    --no-cache-dir

COPY requirements.txt .
# Install heavy ML deps first
RUN pip install --no-cache-dir "paddlex[ocr]" -r requirements.txt

# Explicitly install runpod separately to guarantee it's present
RUN pip install --no-cache-dir runpod

COPY handler.py processor.py download_models.py ./

CMD ["python", "-u", "handler.py"]
