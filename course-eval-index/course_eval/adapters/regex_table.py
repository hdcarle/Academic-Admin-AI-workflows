"""Configurable adapter for evaluation reports that are text tables (one question per line).

Use this when your institution's report is not Campus Labs / Anthology. You describe the
layout with regular expressions in config.yaml (see docs/ADAPTER_GUIDE.md). Example:

adapter: regex_table
adapter_options:
  row_regex: '^(?P<stem>.+?)\\s{2,}(?P<counts>\\d+(?:\\s+\\d+){4})\\s+(?P<mean>\\d\\.\\d+)\\s*$'
  count_order: [5, 4, 3, 2, 1]      # which rating each count column represents, best first
  enrolled_regex: 'Enrolled:\\s*(\\d+)'
  responded_regex: 'Responses:\\s*(\\d+)'
  term_regex: '(?P<season>Fall|Spring|Summer)\\s+(?P<year>\\d{4})'
  course_line_regex: '(?P<course>[A-Z]{3,4}\\s*\\d{3})[-\\s]+(?P<code>\\w+)'
  comments_start_regex: 'Comments'

Only `row_regex` (named groups: stem, counts, optional mean) is required; every other option
falls back to a sensible default or to overrides.yaml.
"""
import re


class Adapter:
    def __init__(self, cfg):
        o = cfg.get("adapter_options", {})
        self.row = re.compile(o["row_regex"], re.M)
        self.enrolled = re.compile(o["enrolled_regex"]) if o.get("enrolled_regex") else None
        self.responded = re.compile(o["responded_regex"]) if o.get("responded_regex") else None
        self.term = re.compile(o["term_regex"]) if o.get("term_regex") else None
        self.course_line = re.compile(o["course_line_regex"]) if o.get("course_line_regex") else None
        self.comments_start = re.compile(o["comments_start_regex"]) if o.get("comments_start_regex") else None
        self.names = cfg.get("instructor", {}).get("name_aliases", [])

    def parse(self, text):
        items = []
        for m in self.row.finditer(text):
            g = m.groupdict()
            counts = [int(x) for x in re.findall(r"\d+", g["counts"])]
            mean = float(g["mean"]) if g.get("mean") else None
            items.append(dict(stem=re.sub(r"\s+", " ", g["stem"]).strip(), counts=counts, reported_mean=mean))
        meta = {}
        if self.term and (m := self.term.search(text)):
            meta["season"], meta["year"] = m.group("season"), int(m.group("year"))
        if self.enrolled and (m := self.enrolled.search(text)):
            meta["enrolled"] = int(m.group(1))
        if self.responded and (m := self.responded.search(text)):
            meta["responded"] = int(m.group(1))
        if self.course_line and (m := self.course_line.search(text)):
            meta["course"] = re.sub(r"\s+", " ", m.group("course")).strip()
            if "code" in m.groupdict() and m.group("code"):
                meta["section_codes"] = [m.group("code")]
        for name in self.names:
            if re.search(re.escape(name), text):
                meta["name_on_report"] = name
                break
        comments = ""
        if self.comments_start and (m := self.comments_start.search(text)):
            comments = text[m.start():]
        return dict(meta=meta, items=items, comments=comments)
