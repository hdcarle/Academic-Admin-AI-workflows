# course-eval-index

Turn a folder of course-evaluation reports (PDFs) into a job-market-ready **teaching workbook**:

- **Course Index**: one row per section and term, with course, format (in-person or online), term, UG or GR, students taught, the average rating for each evaluation item, and an **Avg. Overall**.
- **Summary**: live formulas for students taught overall, by format, by level, and by format × level; average ratings by group, course, and year; career average by item.
- **Student Verbatims**: your best student comments, exact wording, tagged by theme, course, term, format, and level.
- **Method & Notes**: definitions and footnotes, so any number can be defended if a search committee asks.

It was built for an academic job search, where "I taught 1,100 students across 40 sections, and here is every rating" is stronger than a few hand-picked quotes. It works with any evaluation format: a built-in parser handles Campus Labs / Anthology reports, a configurable parser handles other text-table formats, and Claude can write a new parser from one sample report ([docs/ADAPTER_GUIDE.md](docs/ADAPTER_GUIDE.md)).

## What you get

| Sheet | What it does |
| --- | --- |
| Course Index | Course, Format, Term, UG or GR, # taught, one column per evaluation item, Avg. Overall, respondents, response rate, notes, source file. Small samples are highlighted. |
| Summary | Every number is a live Excel formula over Course Index, so editing a row updates the totals. |
| Student Verbatims | Curated quotes from your `verbatims.csv`, checked against the source text so the wording is exact. |
| Method & Notes | How each column was defined, what was excluded from Avg. Overall, and why. |

## Quick start (about 10 minutes with the demo data)

```bash
git clone https://github.com/hdcarle/Academic-Admin-AI-workflows.git
cd Academic-Admin-AI-workflows/course-eval-index
pip install -r requirements.txt

# Run the bundled demo (four made-up reports, no PDFs needed)
python -m course_eval parse --config examples/config.yaml
python -m course_eval build --config examples/config.yaml
```

Open `examples/demo_output/Teaching_Evaluation_Index.xlsx`. Then follow **[SETUP.md](SETUP.md)** to point the tool at your own reports.

## How it works

```
PDF / Word / screenshots  ->  extract  ->  text  ->  parse  ->  data/sections.json  ->  build  ->  workbook
                                                     |                                     ^
                                            adapter (one per report format)        config.yaml + verbatims.csv
```

1. **extract** converts PDFs to text (with OCR for scans), and Word files and screenshots to text for quotes.
2. **parse** reads each report with an *adapter*, maps each question to a column you defined in `config.yaml`, recomputes any mean that is missing from the printed counts, and writes `data/sections.json` and `data/warnings.txt`.
3. **build** writes the workbook. **verify** checks every quote in `verbatims.csv` against the source text.

You edit only three files: `config.yaml` (your columns and rules), `overrides.yaml` (per-file fixes for oddities), and `verbatims.csv` (quotes you choose). Hand-corrected OCR text goes in `text_manual/`.

## Design decisions you should know about

These are the defaults, and each is a setting in `config.yaml` or a note in the workbook.

- **Avg. Overall is calculated, not reported.** Evaluations rarely print a composite. It is the simple average of the item means in the groups you flag `in_avg_overall`, with every input visible on the same row. Summary averages weight each section by its respondents.
- **Only teaching items go into Avg. Overall.** Program- or resource-focused items ("the library was accessible"), comparisons with other courses, and negatively worded items are kept as separate columns, not blended in. See [docs/METHODOLOGY.md](docs/METHODOLOGY.md).
- **Every section you taught counts** in sections and students taught, even with few respondents. Small samples are flagged, not dropped (`min_respondents` controls this).
- **# taught is enrollment**, not the number of survey respondents.
- **Format** is Online if any section code matches a pattern you set (for example, a `D` in `QD1`).
- **UG or GR** comes from the course number and a threshold you set (default 500).

## Privacy

Evaluation reports contain student comments. The `.gitignore` in this repo keeps reports, extracted text, your config, your quotes, and the workbook out of version control. Do not remove those lines. Check your institution's policy on sharing evaluation data in job materials, and remove student names from quotes.

## Repository layout

```
course_eval/            the tool (extract, parse, build, verify)
  adapters/             one file per report format
examples/               runnable demo with fictional data
docs/                   adapter guide, methodology, Claude prompts
skill/SKILL.md          a Claude skill that walks you through setup
config.example.yaml     annotated configuration template
SETUP.md                step-by-step setup for your own reports
```

## Contributing

Adapters for other institutions' formats are the most useful contribution. Add `course_eval/adapters/<name>.py` with a class `Adapter(cfg)` that has a `parse(text)` method, and include a fictional sample report in `examples/`. See the adapter guide.

## License

MIT. See the [LICENSE](../LICENSE) at the root of this repository.
