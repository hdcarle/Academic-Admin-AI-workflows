"""Check that every quote in verbatims.csv appears verbatim in its source text file."""
import os
import re

from .build_workbook import load_verbatims
from .core import norm_quote


def _read_norm(path):
    return norm_quote(open(path, encoding="utf-8").read()) if os.path.exists(path) else ""


def _stem(name):
    return re.sub(r"\s+", " ", os.path.splitext(os.path.basename(name))[0].replace("\u202f", " ")).strip()


def verify(cfg):
    path = os.path.join(cfg["_base"], cfg.get("paths", {}).get("verbatims", "verbatims.csv"))
    rows = load_verbatims(path)
    text_dir = cfg["paths"]["text_dir"]
    # map normalized stems to actual text files (tolerates odd spaces in file names)
    files = {}
    for fn in os.listdir(text_dir):
        if fn.endswith(".txt"):
            files[_stem(fn)] = os.path.join(text_dir, fn)
    cache, bad = {}, 0
    for i, q in enumerate(rows, 1):
        stem = _stem(q.get("source_file", ""))
        if stem not in files:
            if not q.get("source_file"):
                print(f"  #{i}: no source_file given")
            else:
                print(f"  #{i}: no extracted text for '{q['source_file']}' (screenshot? quote it manually and verify by eye)")
            bad += 1
            continue
        if stem not in cache:
            p = files[stem]
            cache[stem] = [_read_norm(p), _read_norm(os.path.join(text_dir, "raw", os.path.basename(p)))]
        needle = norm_quote(q["quote"])
        if not any(needle in hay for hay in cache[stem] if hay):
            print(f"  #{i}: NOT FOUND in {stem}: {q['quote'][:80]}...")
            bad += 1
    print(f"{len(rows)} quote(s) checked, {bad} problem(s).")
    return bad
