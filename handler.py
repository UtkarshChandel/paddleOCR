import runpod
import requests
import tempfile
import os
import base64
from processor import process_annual_report


def handler(job):
    """
    RunPod serverless handler for processing annual report PDFs.

    Input format:
    {
        "pdf_url": "https://..." (required) - URL to download the PDF
        "max_pages": 5 (optional) - Maximum pages to process
        "return_xlsx": false (optional) - Whether to return xlsx files as base64
    }

    Output format:
    {
        "markdown": "# Document content...",
        "stem": "filename",
        "xlsx_count": 3,
        "xlsx_b64": { (if return_xlsx is true)
            "filename_page1_tables.xlsx": "base64encoded...",
            ...
        }
    }
    """
    job_input = job["input"]

    pdf_url = job_input.get("pdf_url")           # Azure Blob SAS URL or any PDF URL
    max_pages = job_input.get("max_pages", None)
    return_xlsx_b64 = job_input.get("return_xlsx", False)

    if not pdf_url:
        return {"error": "Missing required field: pdf_url"}

    # Download PDF to temp file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        response = requests.get(pdf_url, timeout=60)
        response.raise_for_status()
        tmp.write(response.content)
        tmp_path = tmp.name

    try:
        result = process_annual_report(
            pdf_path=tmp_path,
            out_dir="/tmp/output",
            max_pages=max_pages,
        )

        output = {
            "markdown": result["markdown"],
            "stem": result["stem"],
            "xlsx_count": len(result["xlsx_files"]),
        }

        # Optionally encode xlsx files as base64 to return inline
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
