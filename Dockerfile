# Use official PaddlePaddle GPU image (CUDA 12.0)
FROM --platform=linux/amd64 paddlepaddle/paddle:2.6.2-gpu-cuda12.0-cudnn8.9-trt8.6


WORKDIR /app

# System deps for PyMuPDF and OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download PaddleOCR models at build time (avoids cold-start delays)
RUN python -c "from paddleocr import PaddleOCRVL; PaddleOCRVL()"
RUN python -c "from paddlex import create_pipeline; create_pipeline(pipeline='table_recognition_v2')"

COPY handler.py processor.py ./

CMD ["python", "-u", "handler.py"]
