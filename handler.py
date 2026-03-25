import runpod
import requests
import tempfile
import os
import base64
from paddleocr import PaddleOCRVL
from paddlex import create_pipeline

# ✅ Initialize once at startup — runs on RunPod where GPU exists
print("Loading PaddleOCR models...")
vl = PaddleOCRVL()
table_pipeline = create_pipeline(pipeline="table_recognition_v2")
print("Models loaded ✅")


def handler(job):
    job_input = job["input"]

    pdf_url = job_input.get("pdf_url")
    max_pages = job_input.get("max_pages", None)
    return_xlsx_b64 = job_input.get("return_xlsx", False)

    if not pdf_url:
        return {"error": "Missing required field: pdf_url"}

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        response = requests.get(pdf_url, timeout=60)
        response.raise_for_status()
        tmp.write(response.content)
        tmp_path = tmp.name

    try:
        from processor import process_annual_report
        result = process_annual_report(
            pdf_path=tmp_path,
            out_dir="/tmp/output",
            max_pages=max_pages,
            vl=vl,                        # ← pass pre-loaded models
            table_pipeline=table_pipeline, # ← pass pre-loaded models
        )

        output = {
            "markdown": result["markdown"],
            "stem": result["stem"],
            "xlsx_count": len(result["xlsx_files"]),
        }

        if return_xlsx_b64:
            xlsx_encoded = {}
            for path in result["xlsx_files"]:
                name = os.path.basename(path)
                with open(path, "rb") as f:
                    xlsx_encoded[name] = base64.b64encode(f.read()).decode("utf-8")
            output["xlsx_b64"] = xlsx_encoded

        return output

    except Exception as e:
        return {"error": str(e)}
    finally:
        os.unlink(tmp_path)


runpod.serverless.start({"handler": handler})
