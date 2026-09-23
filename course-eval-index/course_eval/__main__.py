"""Command line:  python -m course_eval <command> [--config config.yaml]

Commands: extract | parse | build | verify | run (extract+parse+build)
"""
import argparse
import os

from .build_workbook import build, load_verbatims
from .core import load_config
from .extract import extract_all
from .parse_reports import parse_all
from .verify_quotes import verify


def main():
    ap = argparse.ArgumentParser(prog="course_eval")
    ap.add_argument("command", choices=["extract", "parse", "build", "verify", "run"])
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--force-ocr", nargs="*", default=[], help="file stems to OCR instead of pdftotext")
    a = ap.parse_args()
    cfg = load_config(a.config)
    base = cfg["_base"]
    if a.command in ("extract", "run"):
        extract_all(cfg, force_ocr=set(a.force_ocr))
    if a.command in ("parse", "run"):
        parse_all(cfg)
    if a.command in ("build", "run"):
        import json
        sections = json.load(open(os.path.join(cfg["paths"]["data_dir"], "sections.json"), encoding="utf-8"))
        vpath = os.path.join(base, cfg.get("paths", {}).get("verbatims", "verbatims.csv"))
        out = os.path.join(cfg["paths"]["output_dir"], cfg.get("output_file", "Teaching_Evaluation_Index.xlsx"))
        build(cfg, sections, out, load_verbatims(vpath))
    if a.command == "verify":
        raise SystemExit(1 if verify(cfg) else 0)


if __name__ == "__main__":
    main()
