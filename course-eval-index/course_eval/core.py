"""Shared helpers: config loading, text normalization, item mapping, mean calculation,
and turning parsed reports into normalized section records."""
import json
import os
import re

import yaml

DEFAULT_SEASON_ORDER = ["Winter", "Spring", "May", "Summer I", "Summer II", "Fall"]


def load_yaml(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_config(path):
    cfg = load_yaml(path)
    base = os.path.dirname(os.path.abspath(path))
    cfg["_base"] = base
    for key in ("text_dir", "pdf_dir", "output_dir", "data_dir"):
        v = cfg.get("paths", {}).get(key)
        if v and not os.path.isabs(v):
            cfg["paths"][key] = os.path.normpath(os.path.join(base, v))
    return cfg


def norm_stem(s):
    """Normalize a question stem for regex matching (de-hyphenate line wraps, lowercase)."""
    s = re.sub(r"-\s+", "", s)
    return re.sub(r"\s+", " ", s).lower().strip()


def norm_quote(s):
    """Normalize text for verbatim checking: lowercase alphanumerics only, with ligature
    letters removed so PDF ligature loss (fi, fl, ff...) cannot cause false mismatches."""
    s = s.lower()
    for lig in ("ffi", "ffl", "ff", "fi", "fl"):
        s = s.replace(lig, "")
    return re.sub(r"[^a-z0-9]", "", s)


def item_index(cfg):
    """Return the ordered list of configured items with compiled match patterns."""
    out = []
    for it in cfg.get("items", []):
        d = dict(it)
        d["_rx"] = re.compile(d["match"]) if d.get("match") else None
        out.append(d)
    return out


def map_stem(stem, items):
    n = norm_stem(stem)
    for it in items:
        if it["_rx"] and it["_rx"].search(n):
            return it["key"]
    return None


def weighted_mean(counts, weights):
    c = counts[: len(weights)]
    n = sum(c)
    if not n:
        return None, 0
    return sum(a * b for a, b in zip(c, weights)) / n, n


def compute_item(counts, scales, reported, tol=0.03):
    """Pick the scale whose calculated mean matches the mean printed on the report.
    Returns (mean, n, scale_index, warning)."""
    cands = []
    for i, w in enumerate(scales):
        m, n = weighted_mean(counts, w)
        if m is not None:
            cands.append((m, n, i))
    if not cands:
        return None, 0, None, None
    if reported is None:
        return cands[0][0], cands[0][1], cands[0][2], None
    for m, n, i in cands:
        if abs(m - reported) <= tol:
            return m, n, i, None
    m, n, i = cands[0]
    return m, n, i, f"calculated mean {m:.2f} differs from printed {reported}"


def season_year(term_label):
    m = re.match(r"(.+?)\s+(\d{4})$", term_label.strip())
    return (m.group(1), int(m.group(2))) if m else (None, None)


def level_for(course, threshold):
    nums = re.findall(r"\d+", course)
    if not nums:
        return "UG"
    return "GR" if int(nums[0]) >= threshold else "UG"


def build_sections(parsed, cfg, overrides):
    """parsed: {stem: ParsedReport dict}. Returns (sections, warnings)."""
    items_cfg = item_index(cfg)
    by_key = {i["key"]: i for i in items_cfg}
    sec_cfg = cfg.get("sections", {})
    online_rx = re.compile(sec_cfg.get("online_code_regex", r"D"))
    threshold = sec_cfg.get("graduate_min_course_number", 500)
    season_rules = sec_cfg.get("season_overrides", [])
    surveys = cfg.get("surveys", [])
    tol = cfg.get("mean_tolerance", 0.06)  # printed means are often rounded to 1 decimal
    sections, warnings = [], []

    for stem, rep in parsed.items():
        ov = overrides.get(stem, {})
        if ov.get("exclude"):
            continue
        meta = dict(rep["meta"])
        meta.update({k: v for k, v in ov.items() if k in (
            "course", "section_codes", "season", "year", "enrolled", "responded",
            "name_on_report", "level", "format")})
        w = []
        codes = meta.get("section_codes") or []
        course = meta.get("course")
        if not course:
            w.append("course not found; add it in overrides.yaml")
            course = "UNKNOWN"
        season, year = meta.get("season"), meta.get("year")
        if not season or not year:
            w.append("term not found; add season/year in overrides.yaml")
        for rule in season_rules:
            if any(re.search(rule["code_regex"], c) for c in codes):
                season = rule["season"]
        fmt = meta.get("format") or ("Online" if any(online_rx.search(c) for c in codes) else "In-person")
        level = meta.get("level") or level_for(course, threshold)
        rep_level = meta.get("level_on_report")
        if rep_level and rep_level != level and "level" not in ov:
            w.append(f"level on report ({rep_level}) differs from course-number rule ({level})")
        # items
        vals = {}
        for it in rep["items"]:
            key = map_stem(it["stem"], items_cfg)
            if key is None:
                if not any(re.search(p, norm_stem(it["stem"])) for p in cfg.get("ignore_stems", [])):
                    w.append(f"unmapped question: {it['stem'][:70]}")
                continue
            scales = by_key[key].get("scales") or cfg.get("default_scales") or [[5, 4, 3, 2, 1]]
            m, n, si, warn = compute_item(it["counts"], scales, it.get("reported_mean"), tol)
            if m is None:
                continue
            if warn:
                w.append(f"{key}: {warn}")
            value = it["reported_mean"] if it.get("reported_mean") is not None else round(m, 2)
            if by_key[key].get("reverse"):  # negatively worded item: flip so higher is always better
                w0 = scales[0]
                value = round(max(w0) + min(w0) - value, 2)
            vals[key] = dict(mean=value, n=n, counts=it["counts"], scale=si)
        for k, v in ov.get("item_values", {}).items():
            vals[k] = dict(mean=v, n=None, counts=None, scale=None, manual=True)
        # survey version
        survey = surveys[-1]["id"] if surveys else "default"
        for s in surveys:
            if any(k in vals for k in s.get("detect_keys", [])):
                survey = s["id"]
                break
        if meta.get("enrolled") is None or meta.get("responded") is None:
            w.append("enrolled/responded missing; add them in overrides.yaml")
        sections.append(dict(
            file=stem, course=course, section_codes=codes,
            section="/".join(dict.fromkeys(codes)) if codes else "",
            format=fmt, season=season, year=year, level=level,
            enrolled=meta.get("enrolled"), responded=meta.get("responded"),
            name_on_report=meta.get("name_on_report"), survey=survey, items=vals,
            warnings=w))
        for msg in w:
            warnings.append(f"{stem}: {msg}")
    # possible parse misses: items that most sections of the same survey version have, but this one lacks
    by_survey = {}
    for x in sections:
        by_survey.setdefault(x["survey"], []).append(x)
    for sv, group in by_survey.items():
        if len(group) < 4:
            continue
        common = [k for k in {k for x in group for k in x["items"]}
                  if sum(k in x["items"] for x in group) >= 0.8 * len(group)]
        for x in group:
            miss = sorted(k for k in common if k not in x["items"] and not by_key[k].get("optional"))
            if miss:
                msg = f"{x['file']}: no value for {', '.join(miss)} (all 'Does Not Apply', or a parse/OCR miss - check the PDF)"
                x["warnings"].append(msg)
                warnings.append(msg)
    order = {s: i for i, s in enumerate(cfg.get("season_order", DEFAULT_SEASON_ORDER))}
    sections.sort(key=lambda x: (x["year"] or 0, order.get(x["season"], 99), x["course"], x["section"]))
    return sections, warnings


def dump_json(obj, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
