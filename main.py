import sys
import fitz  # PyMuPDF
from pathlib import Path
from paddleocr import PaddleOCRVL
from paddlex import create_pipeline


def process_annual_report(pdf_path: str, out_dir: str = "./output", max_pages: int = None):
    pdf = Path(pdf_path)
    if not pdf.exists():
        print(f"[ERROR] File not found: {pdf_path}")
        sys.exit(1)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = pdf.stem

    print(f"\n📄 Processing: {pdf.name}")
    if max_pages:
        print(f"⚠️  Limited to first {max_pages} pages")
    print("─" * 50)

    # ── Step 1: Full document → Markdown ──────────────
    print("▸ Running PaddleOCR-VL for full document markdown...")
    vl = PaddleOCRVL()
    pages = list(vl.predict(input=str(pdf)))
    pages = pages[:max_pages] if max_pages else pages

    structured = vl.restructure_pages(
        pages,
        merge_tables=True,
        relevel_titles=True,
        concatenate_pages=True,
    )
    for res in structured:
        res.save_to_markdown(save_path=str(out))
        res.save_to_json(save_path=str(out))
    print(f"  ✅ Markdown saved → {out}/{stem}.md")

    # ── Step 2: Tables → XLSX (per page) ──────────────
    print("▸ Extracting tables to XLSX...")
    table_pipeline = create_pipeline(pipeline="table_recognition_v2")

    doc = fitz.open(str(pdf))
    total_pages = len(doc)
    page_limit = min(max_pages, total_pages) if max_pages else total_pages
    print(f"  Processing {page_limit}/{total_pages} pages...")

    for i in range(page_limit):
        print(f"  → Page {i + 1}/{page_limit}", end="\r")
        img_path = f"/tmp/{stem}_p{i}.png"
        doc[i].get_pixmap(dpi=200).save(img_path)

        results = table_pipeline.predict(
            input=img_path,
            use_doc_orientation_classify=True,
            use_doc_unwarping=True,
        )
        for res in results:
            xlsx_out = str(out / f"{stem}_page{i + 1}_tables.xlsx")
            res.save_to_xlsx(xlsx_out)

    print(f"\n  ✅ XLSX files saved → {out}/")
    print(f"\n🎉 Done! Outputs in: {out.resolve()}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run main.py <path-to-pdf> [max_pages]")
        print("  e.g: uv run main.py input/report.pdf 5")
        sys.exit(1)

    pdf_input = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else None

    process_annual_report(pdf_path=pdf_input, max_pages=max_pages)
