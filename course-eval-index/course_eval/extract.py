"""Turn PDFs, Word files and images into plain text (with OCR fallback)."""
import glob
import os
import re
import shutil
import subprocess
import tempfile


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def pdf_text(path):
    if not shutil.which("pdftotext"):
        raise SystemExit("pdftotext not found. Install poppler (see SETUP.md).")
    return _run(["pdftotext", "-layout", path, "-"]).stdout


def pdf_text_raw(path):
    """Reading-order text (no layout columns). Used only to verify quotes from two-column reports."""
    return _run(["pdftotext", path, "-"]).stdout


def ocr_pdf(path):
    if not (shutil.which("tesseract") and shutil.which("pdftoppm")):
        raise SystemExit("OCR needs tesseract and pdftoppm (see SETUP.md).")
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        _run(["pdftoppm", "-r", "300", "-png", path, os.path.join(tmp, "p")])
        for img in sorted(glob.glob(os.path.join(tmp, "p*.png"))):
            out.append(_run(["tesseract", img, "-", "--psm", "6"]).stdout)
    return "\n".join(out)


def image_text(path):
    if not shutil.which("tesseract"):
        raise SystemExit("tesseract not found (see SETUP.md).")
    return _run(["tesseract", path, "-", "--psm", "6"]).stdout


def docx_text(path):
    import docx  # python-docx
    d = docx.Document(path)
    return "\n".join(p.text for p in d.paragraphs)


def extract_all(cfg, force_ocr=(), verbose=True):
    src, dst = cfg["paths"]["pdf_dir"], cfg["paths"]["text_dir"]
    os.makedirs(dst, exist_ok=True)
    n = 0
    for path in sorted(glob.glob(os.path.join(src, "**", "*"), recursive=True)):
        ext = os.path.splitext(path)[1].lower()
        stem = os.path.splitext(os.path.basename(path))[0].strip()
        if ext not in (".pdf", ".docx", ".png", ".jpg", ".jpeg"):
            continue
        target = os.path.join(dst, stem + ".txt")
        if ext == ".pdf":
            raw_target = os.path.join(dst, "raw", stem + ".txt")
            if not os.path.exists(raw_target):
                os.makedirs(os.path.dirname(raw_target), exist_ok=True)
                with open(raw_target, "w", encoding="utf-8") as fh:
                    fh.write(pdf_text_raw(path))
        if os.path.exists(target) and os.path.getmtime(target) >= os.path.getmtime(path) and stem not in force_ocr:
            continue
        if ext == ".pdf":
            text = pdf_text(path)
            scanned = len(text.strip()) < 200
            forced = stem in force_ocr or stem in cfg.get("force_ocr_files", [])
            if scanned or forced:
                if verbose:
                    print(f"  OCR fallback: {stem}")
                text = ocr_pdf(path)
        elif ext == ".docx":
            text = docx_text(path)
        else:
            text = image_text(path)
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(text)
        n += 1
        if verbose:
            print(f"  extracted {stem}")
    print(f"{n} file(s) converted to text in {dst}")
