# Adapter guide: supporting your institution's report format

An **adapter** reads the text of one evaluation report and returns three things:

```python
{
  "meta":  {"course": "BUS 101", "section_codes": ["QD1"], "season": "Fall", "year": 2023,
            "enrolled": 30, "responded": 22, "name_on_report": "Alex Rivera"},   # any key may be missing
  "items": [{"stem": "The instructor treated students with respect.",
             "counts": [17, 4, 1, 0, 0],       # responses per option, best option first
             "reported_mean": 4.7}],           # the mean printed on the report, or None
  "comments": "text after the Qualitative heading"    # optional
}
```

Everything else (mapping questions to columns, computing means, format, level, workbook) is shared, so an adapter is small.

## Option 1: use `regex_table` (no code)

If each question is one line of text like

```
Q3 - The instructor gave feedback in a timely manner.     9   6   3   1   0    3.9
```

set this in `config.yaml`:

```yaml
adapter: regex_table
adapter_options:
  row_regex: '^\s*(?P<stem>.+?)\s{2,}(?P<counts>\d+(?:\s+\d+){4})\s+(?P<mean>\d\.\d+)\s*$'
  term_regex: '(?P<season>Fall|Spring|Summer)\s+(?P<year>\d{4})'
  enrolled_regex: 'Enrolled:\s*(\d+)'
  responded_regex: 'Responses:\s*(\d+)'
  course_line_regex: '(?P<course>[A-Z]{3,4}\s*\d{3})[-\s]+(?P<code>\w+)'
  comments_start_regex: 'Comments'
```

Test each regex on your text at regex101.com (choose the Python flavor). Only `row_regex` is required. Missing metadata can go in `overrides.yaml`.

## Option 2: ask Claude to write an adapter

Give Claude one sample report as text and this prompt:

> I want to add a new adapter to course-eval-index (a Python project). Read `course_eval/adapters/anthology_campuslabs.py` and `regex_table.py` for the interface. Below is the text of one evaluation report from my institution (student names removed). Write `course_eval/adapters/my_institution.py` with a class `Adapter(cfg)` and a method `parse(text)` that returns `{"meta", "items", "comments"}` as described in `docs/ADAPTER_GUIDE.md`. Then run it against the sample and show me the items it found, with counts and means. Point out any rows it could not read.

Then set `adapter: my_institution` in `config.yaml`. Ask Claude to check three things against the PDF: the number of questions found, the counts for two questions, and the enrolled and responded numbers.

## Option 3: write it yourself

Copy `regex_table.py` and change `parse`. Rules of thumb:

- Return **counts per option, best first** (for example Strongly Agree first). Do not include "Does Not Apply" in `counts[:5]`. It may follow in the list.
- If the report prints a mean, return it as `reported_mean`. The tool uses it to choose between candidate scales and to catch misreads.
- Return question text as it appears (wrapped lines joined with spaces).
- If a report has two layouts, try one and fall back to the other, as the Campus Labs adapter does.
- Do not guess metadata. Leave a key out, and the warning tells the user to add an override.

## Scales

Most evaluations use 5 points (5 = Strongly Agree). `default_scales: [[5,4,3,2,1]]` applies weights to the first five counts. If a question uses different options, set `scales` on the item. You can list more than one candidate, and the one whose calculated mean matches the printed mean is used:

```yaml
- {key: navigation, label: "...", group: online, match: '...', scales: [[4,3,2,1],[4,3,2,1,0]]}
```

## Testing an adapter

1. Save a fictional sample report in `examples/sample_reports/`.
2. Run `python -m course_eval parse --config examples/config.yaml` and read `demo_data/warnings.txt`.
3. Open `demo_data/sections.json` and compare three sections with the sample.
