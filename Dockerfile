FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.10 python3-pip python3.10-dev \
    libgl1-mesa-glx libglib2.0-0 wget \
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3.10 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# ✅ Correct version + correct index URL for CUDA 11.8
RUN pip install --no-cache-dir \
    paddlepaddle-gpu==3.0.0 \
    -i https://www.paddlepaddle.org.cn/packages/stable/cu118/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download models at build time
RUN python -c "from paddleocr import PaddleOCRVL; PaddleOCRVL()"
RUN python -c "from paddlex import create_pipeline; create_pipeline(pipeline='table_recognition_v2')"

COPY handler.py processor.py ./

CMD ["python", "-u", "handler.py"]
