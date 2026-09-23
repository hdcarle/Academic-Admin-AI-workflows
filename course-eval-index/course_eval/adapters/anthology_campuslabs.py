"""Adapter for Campus Labs / Anthology course-evaluation reports (text extracted with pdftotext).

Handles the two layouts seen in these reports:
  1. Classic rows:   "Q6 - The professor was prepared   100% (10)  0% (0) ...  10  0  0  5"
  2. Summary layout: percentages on one line, "(count)" values on the next line.

It returns raw counts per question plus the mean printed on the report (when present).
Question-to-column mapping and scale handling happen later, driven by config.yaml.
"""
import re

PCT = re.compile(r"\d+(?:\.\d+)?%\s*\(\d+\)")
CP = re.compile(r"(\d+(?:\.\d+)?)%\s*\((\d+)\)")
PCTT = re.compile(r"\d+(?:\.\d+)?%")
CNT = re.compile(r"\((\d+)\)")

DEFAULT_TERM = (r"(?P<season>Winter|Fall|Spring|Summer I{1,2}|May)\s+(?:Semester\s+)?"
                r"(?P<year>\d{4})(?:\s+(?P<level>UG|GR))?")


class Adapter:
    def __init__(self, cfg):
        opts = cfg.get("adapter_options", {})
        sec = cfg.get("sections", {})
        self.course_rx = re.compile(sec.get("course_regex", r"[A-Z]{2,5}\s*\d{3}"))
        self.code_rx = re.compile(sec.get("section_code_regex", r"\(([A-Z]{1,3}\d)\)"))
        self.term_rx = re.compile(opts.get("term_regex", DEFAULT_TERM))
        self.skip_rx = re.compile(opts.get("skip_line_regex", r"\s*Overall"))
        self.names = cfg.get("instructor", {}).get("name_aliases", [])
        self.header_lines = opts.get("header_lines", 9)

    # ---- layout 1
    def _classic(self, lines):
        out, i = [], 0
        while i < len(lines):
            line = lines[i]
            m = PCT.search(line)
            if m and not self.skip_rx.match(line) and not self.course_rx.match(line.strip() or " "):
                left = line[: m.start()].strip()
                tail = line[line.rfind(")") + 1:].split()
                cont, j = [], i + 1
                while j < len(lines):
                    s = lines[j]
                    if not s.strip() or PCT.search(s):
                        break
                    if re.search(r"Strongly|Agree|Disagree|Standard|Mean|Deviation", s):
                        break
                    if s.strip().startswith(("https://", "Qualitative", "Please", "Quantitative")):
                        break
                    cont.append(s[: m.start()].strip() if len(s) > m.start() else s.strip())
                    j += 1
                stem = (left + " " + " ".join(c for c in cont if c)).strip()
                counts = [int(b) for _, b in CP.findall(line)]
                mean = None
                try:
                    mean = float(tail[-1])
                except (ValueError, IndexError):
                    pass
                out.append(dict(stem=stem, counts=counts, reported_mean=mean))
            i += 1
        return out

    # ---- layout 2
    def _summary(self, lines):
        out, i = [], 0
        while i < len(lines) - 1:
            p, c = PCTT.findall(lines[i]), CNT.findall(lines[i + 1])
            if len(p) >= 4 and len(c) >= 4 and len(p) == len(c):
                pre1 = re.split(r"\d+(?:\.\d+)?%", lines[i])[0].strip()
                pre2 = re.split(r"\s\(\d", lines[i + 1])[0]
                pre2 = re.sub(r"\s+A\s*$", "", pre2.strip()).strip()
                parts, j = [pre1, pre2], i + 2
                while (j < len(lines) and lines[j].strip() and not PCTT.findall(lines[j])
                       and not re.search(r"Strongly|Neither|Agree|https|Page \d", lines[j])):
                    parts.append(re.sub(r"\s+A\s*$", "", lines[j].strip()))
                    j += 1
                out.append(dict(stem=" ".join(x for x in parts if x),
                                counts=[int(x) for x in c], reported_mean=None))
                i = j
                continue
            i += 1
        return out

    # ---- metadata
    def _meta(self, text, lines):
        meta = {}
        head = "\n".join(lines[: self.header_lines])
        m = self.term_rx.search(text)
        if m:
            meta["season"], meta["year"] = m.group("season"), int(m.group("year"))
            if "level" in m.groupdict() and m.group("level"):
                meta["level_on_report"] = m.group("level")
        m = re.search(r"(\d+)\s*\|\s*Students Enrolled", text)
        if m:
            meta["enrolled"] = int(m.group(1))
        m = re.search(r"(\d+)\s*\|\s*Students Responded", text)
        if m:
            meta["responded"] = int(m.group(1))
        if "enrolled" not in meta:  # summary layout: "COURSE (D1): Title | Released | 32 | 24 | 75%"
            m = re.search(r"\|\s*Released\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", text)
            if m:
                meta["enrolled"], meta["responded"] = int(m.group(1)), int(m.group(2))
        m = re.search(r"^\s*(" + self.course_rx.pattern + r")\s*\(", text, re.M)
        if m:
            meta["course"] = re.sub(r"\s+", " ", m.group(1)).strip()
        before_term = head.split("Semester")[0] if "Semester" in head else head
        codes = self.code_rx.findall(before_term)
        if not codes and meta.get("course"):
            codes = self.code_rx.findall(text[:400])[:1]
        meta["section_codes"] = list(dict.fromkeys(codes))
        for name in self.names:
            if re.search(re.escape(name), text):
                meta["name_on_report"] = name
                break
        return meta

    def parse(self, text):
        lines = text.split("\n")
        items = self._classic(lines) or self._summary(lines)
        qi = next((i for i, l in enumerate(lines) if l.strip().startswith("Qualitative")), None)
        comments = "\n".join(lines[qi:]) if qi is not None else ""
        return dict(meta=self._meta(text, lines), items=items, comments=comments)
