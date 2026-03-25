FROM ccr-2vdh3abv-pub.cnc.bj.baidubce.com/paddlepaddle/paddle:3.0.0-gpu-cuda12.6-cudnn9.5-trt10.5

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# PaddlePaddle 3.0.0 is already in the base image — just install your app deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY handler.py processor.py ./

CMD ["python", "-u", "handler.py"]
