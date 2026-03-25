import os
from pathlib import Path

MODEL_DIR = Path(os.environ.get("PADDLEX_HOME", "/root/.paddlex"))

def download_if_needed():
    vl_path = MODEL_DIR / "official_models" / "PaddleOCR-VL-1.5"
    table_path = MODEL_DIR / "official_models" / "PP-TableFormer"

    if vl_path.exists() and table_path.exists():
        print("Models already cached ✅")
        return

    print("Downloading models for first time (will be cached)...")
    from paddleocr import PaddleOCRVL
    from paddlex import create_pipeline
    PaddleOCRVL()
    create_pipeline(pipeline="table_recognition_v2")
    print("Models downloaded and cached ✅")

if __name__ == "__main__":
    download_if_needed()