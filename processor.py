import fitz
from pathlib import Path
from paddleocr import PaddleOCRVL
from paddlex import create_pipeline


def process_annual_report(pdf_path: str, out_dir: str = "/tmp/output", max_pages: int = None) -> dict:
    """
    Process an annual report PDF: extract markdown and tables.

    Args:
        pdf_path: Path to the PDF file
        out_dir: Directory to save output files
        max_pages: Maximum number of pages to process (None for all)

    Returns:
        Dictionary with markdown content, xlsx file paths, and stem
    """
    pdf = Path(pdf_path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = pdf.stem

    # ── Step 1: Full document → Markdown ──────────────────────
    vl = PaddleOCRVL()
    pages = list(vl.predict(input=str(pdf)))
    pages = pages[:max_pages] if max_pages else pages

    structured = vl.restructure_pages(
        pages,
        merge_tables=True,
        relevel_titles=True,
        concatenate_pages=True,
    )

    markdown_content = None
    for res in structured:
        res.save_to_markdown(save_path=str(out))
        res.save_to_json(save_path=str(out))

    md_file = out / f"{stem}.md"
    if md_file.exists():
        markdown_content = md_file.read_text(encoding="utf-8")

    # ── Step 2: Tables → XLSX (per page) ───────────────────────
    table_pipeline = create_pipeline(pipeline="table_recognition_v2")
    doc = fitz.open(str(pdf))
    total_pages = len(doc)
    page_limit = min(max_pages, total_pages) if max_pages else total_pages

    xlsx_paths = []
    for i in range(page_limit):
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
            xlsx_paths.append(xlsx_out)

    return {
        "markdown": markdown_content,
        "xlsx_files": xlsx_paths,
        "stem": stem,
    }
