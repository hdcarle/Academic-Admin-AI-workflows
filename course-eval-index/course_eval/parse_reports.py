"""Parse extracted text into data/sections.json (+ data/warnings.txt and data/comments/*.txt)."""
import glob
import os

from .adapters import get_adapter
from .core import build_sections, dump_json, load_yaml


def parse_all(cfg, verbose=True):
    text_dir, data_dir = cfg["paths"]["text_dir"], cfg["paths"]["data_dir"]
    adapter = get_adapter(cfg.get("adapter", "anthology_campuslabs"), cfg)
    overrides = load_yaml(os.path.join(cfg["_base"], "overrides.yaml"))
    skip = set(cfg.get("skip_files", []))
    parsed = {}
    os.makedirs(os.path.join(data_dir, "comments"), exist_ok=True)
    for path in sorted(glob.glob(os.path.join(text_dir, "*.txt"))):
        stem = os.path.splitext(os.path.basename(path))[0]
        if stem in skip:
            continue
        manual = os.path.join(cfg["_base"], "text_manual", stem + ".txt")  # hand-corrected text wins
        text = open(manual if os.path.exists(manual) else path, encoding="utf-8").read()
        rep = adapter.parse(text)
        if not rep["items"]:  # not an evaluation report (e.g., an email or Word doc): keep as comment source only
            if verbose:
                print(f"  no rating rows in {stem} (kept as comment source only)")
            continue
        parsed[stem] = rep
        with open(os.path.join(data_dir, "comments", stem + ".txt"), "w", encoding="utf-8") as fh:
            fh.write(rep["comments"])
    sections, warnings = build_sections(parsed, cfg, overrides)
    dump_json(sections, os.path.join(data_dir, "sections.json"))
    with open(os.path.join(data_dir, "warnings.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(warnings) + ("\n" if warnings else ""))
    print(f"{len(sections)} sections parsed; {len(warnings)} warning(s) written to data/warnings.txt")
    for wmsg in warnings[:25]:
        print("  !", wmsg)
    if len(warnings) > 25:
        print(f"  ... and {len(warnings) - 25} more")
    tot = sum(s["enrolled"] or 0 for s in sections)
    print(f"Sanity check: {len(sections)} sections, {tot} students enrolled.")
    return sections
