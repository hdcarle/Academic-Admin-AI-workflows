# Setup guide

This guide gets the tool running on your own course evaluations. Plan on 30 to 60 minutes the first time, mostly spent listing your evaluation questions. After that, each new semester takes a few minutes.

There are two ways through: **with Claude** (recommended if you are not a programmer) and **by hand**. Both produce the same workbook.

## 0. What you need

- Python 3.9 or newer.
- Your evaluation reports as **PDFs** saved from your institution's evaluation system (one file per section, or one per combined section).
- For scanned or garbled PDFs only: Tesseract (OCR).
- Optional, for student comments: Word documents, screenshots of emails or discussion posts.

Install the system tools:

| Tool | macOS (Homebrew) | Windows | Linux (Debian/Ubuntu) |
| --- | --- | --- | --- |
| Poppler (`pdftotext`) | `brew install poppler` | Download poppler for Windows and add its `bin` folder to PATH | `sudo apt install poppler-utils` |
| Tesseract (OCR, optional) | `brew install tesseract` | Installer from the UB Mannheim build | `sudo apt install tesseract-ocr` |

Then, in the repository folder:

```bash
pip install -r requirements.txt
```

Check it works: `python -m course_eval parse --config examples/config.yaml` should print `4 sections parsed`.

## 1. Create your working folder

Keep your real data **outside** any folder you push to GitHub, or rely on the included `.gitignore`. The simplest layout is inside your clone:

```
course-eval-index/
  reports/            <- put your evaluation PDFs here (and Word files / screenshots of comments)
  config.yaml         <- you create this (step 2)
  overrides.yaml      <- optional (step 5)
  verbatims.csv       <- optional (step 7)
```

Copy the template: `cp config.example.yaml config.yaml`.

## 2. Tell the tool about your institution (config.yaml)

Open `config.yaml` and edit these sections, top to bottom. Every key has a comment.

1. **instructor** and **institution**: your name as it should appear, and any names that appear on older reports (for example, a name change).
2. **sections**: three rules that create the columns most search committees care about.
   - `course_regex`: what a course code looks like (for example `[A-Z]{2,5}\s*\d{3}` matches `BUS 101`).
   - `online_code_regex`: a section is **Online** if any of its section codes matches this pattern. Many institutions put a `D` in the section code for distance or online sections. Check your registrar's convention.
   - `graduate_min_course_number`: course numbers at or above this are **GR**, below are **UG**. The common default is 500.
3. **paths**: leave the defaults unless you keep your files elsewhere.

## 3. Choose your report format (adapter)

Set `adapter:` in `config.yaml`.

- `anthology_campuslabs` if your reports look like Campus Labs or Anthology (rows such as `Q6 - The professor was prepared   100% (10)  0% (0) ...`).
- `regex_table` if each question is one line of text with counts and a mean. You describe the line with a regex (see the comments in `config.example.yaml` and [docs/ADAPTER_GUIDE.md](docs/ADAPTER_GUIDE.md)).
- Anything else: ask Claude to write an adapter from one sample report (next section).

To see what your reports look like as text, run step 4 first and open a file in `text/`.

## 4. Extract text

Put your PDFs in `reports/`, then:

```bash
python -m course_eval extract
```

Text files appear in `text/`. Scanned PDFs (almost no text) are OCR'd automatically. If a PDF's text is garbled (letters mixed up, missing numbers), re-run it with OCR and check it by eye:

```bash
python -m course_eval extract --force-ocr "BUS 101 Q1 FA23"
```

OCR can misread a digit. Check the OCR text against the PDF, and save a corrected copy as `text_manual/<same file name>.txt`. The tool always prefers a file in `text_manual/` over the extracted text, so your corrections survive every rerun.

## 5. List your evaluation questions (items)

This is the most important step, and the one that decides how strong your workbook looks. Open one text file and list each rating question. In `config.yaml`, add one entry under `items` per question you want as a column:

```yaml
items:
  - {key: respect, label: "The instructor treated students with respect.", group: teaching, match: 'treated students with respect'}
```

- `key`: a short unique name you make up.
- `label`: the column heading.
- `match`: a regex that matches the question's text (lowercase). Use a distinctive phrase.
- `group`: which block of columns it belongs to (defined under `groups`).

**Put only teaching-quality questions in the group flagged `in_avg_overall`.** Put program- or resource-focused questions, comparisons with other courses, and negatively worded questions in a different group, so they show up for transparency but do not affect Avg. Overall. [docs/METHODOLOGY.md](docs/METHODOLOGY.md) explains how to sort questions.

If your institution changed its survey form over the years, define one `surveys` entry per form. List the old one first with `detect_keys` (any item key that only exists on that form). Set `summary.avg_overall_survey` if you want summary averages to use only one form.

Now parse:

```bash
python -m course_eval parse
```

Read `data/warnings.txt` and fix each line. Typical warnings and fixes:

| Warning | Fix |
| --- | --- |
| `unmapped question: ...` | Add an item with a `match` for it, or add a phrase to `ignore_stems` if it is not a rating (for example, a demographic question). |
| `course not found`, `term not found` | Add the value in `overrides.yaml` (below). |
| `enrolled/responded missing` | Add them in `overrides.yaml`. |
| `no value for ...` | Usually every respondent chose "Does Not Apply". If the section has plenty of respondents, the PDF text was misread: open it and check. |
| `calculated mean ... differs from printed` | The response counts and the printed mean disagree. Check the PDF, or list a second candidate scale under the item's `scales`. |

### overrides.yaml (per-file fixes)

Create `overrides.yaml` next to `config.yaml`. The key is the file name without extension:

```yaml
"BUS 101 Q1 FA23":
  enrolled: 30
  responded: 22
"BUS 520 D1 FA24":
  season: Fall
  year: 2024
  course: BUS 520
  section_codes: [D1]
  item_values: {respect: 4.5}     # hand-entered value for an item the parser could not read
  # exclude: true                 # leave this file out entirely
```

Use it sparingly, and mention any hand-entered values in `method_notes` so the workbook stays honest.

**Check the totals.** `parse` prints how many sections and students it found. Compare with your own records before you continue.

## 6. Build the workbook

```bash
python -m course_eval build
```

The workbook is written to `output/Teaching_Evaluation_Index.xlsx`. It has formulas, so open it in Excel or LibreOffice. If your viewer shows empty cells, recalculate (LibreOffice: Data > Calculate > Recalculate Hard).

Spot-check three or four rows against the PDFs before you send it anywhere.

## 7. Add your best student comments (verbatims)

Create `verbatims.csv` with these columns:

```csv
quote,theme,top_pick,course,term,format,level,source_type,source_file
"The case studies helped me connect ideas to real companies.",Real-world learning,y,BUS 101,Fall 2023,,,Course evaluation,BUS 101 Q1 FA23.pdf
```

- `quote`: copy the text exactly, including typos. Remove student names.
- `theme`: a short category, such as "Career impact" or "Feedback and responsiveness". Group your quotes into five to eight themes.
- `top_pick`: `y` for the few you would use first.
- `course` and `term` (for example `Fall 2023`) let the tool fill in Format and UG or GR. Leave `format` and `level` blank.
- `source_file`: the file the quote came from. Word documents and screenshots work if you put them in `reports/` and run `extract`.

Then check that every quote is verbatim:

```bash
python -m course_eval verify
```

It normalizes spacing and PDF ligature losses (`fi`, `fl`, `ff`), and it also checks against a reading-order copy of the PDF for two-column layouts. Fix or remove any quote it cannot find. Screenshots are OCR'd, so verify screenshot quotes by eye.

To find good quotes fast, ask Claude to read `data/comments/` and propose candidates by theme (see [docs/PROMPTS.md](docs/PROMPTS.md)), then verify them.

## 8. Each new semester

1. Drop the new PDFs in `reports/`.
2. `python -m course_eval run` (extract, parse, build).
3. Read `data/warnings.txt`, add any new fixes to `overrides.yaml`, and rerun `build`.
4. Add new quotes to `verbatims.csv` and run `verify`.

Nothing else changes: the same config produces the same columns, so earlier rows do not move.

---

## Doing this with Claude (no coding)

The README's **Option 1** has the full steps. In short:

1. Install the skill: copy `skill/course-eval-index/` to `~/.claude/skills/` (Claude Code), or, with no terminal, upload `skill/course-eval-index.zip` under Settings > Skills (Claude desktop app or claude.ai).
2. Open Claude Code in this folder, or connect this folder in Cowork.
3. Paste: **"Set up course-eval-index for my course evaluations. The tool is in this folder, and my evaluation PDFs are in `reports/`. Follow the course-eval-index skill. Look at one of my reports, then ask me the three rules (how to tell a section is online, where graduate level starts, what a course code looks like). Propose my list of evaluation questions and which of them count toward Avg. Overall, and let me confirm before building. Then build my workbook and check the section and student totals with me."**

Claude will:

1. Read one of your reports and ask you the three rules in step 2 (online code, graduate threshold, course pattern).
2. Propose your `items` list, mark which ones belong in Avg. Overall, and ask you to confirm.
3. Write `config.yaml`, extract and parse everything, and walk you through each line of `warnings.txt`.
4. If your report format is not Campus Labs, write an adapter from one sample (see [docs/ADAPTER_GUIDE.md](docs/ADAPTER_GUIDE.md)).
5. Build the workbook and check the totals with you.

## Troubleshooting

- **`pdftotext not found`**: install Poppler (step 0) and restart your terminal.
- **`0 sections parsed` or `no rating rows in ...`**: the adapter does not recognize your layout. Open a text file from `text/` and compare it with the adapter guide.
- **Numbers look shifted by one column**: your scale has a different order. Set `default_scales` (for example `[[1,2,3,4,5]]` if your reports list Strongly Disagree first) or a per-item `scales`.
- **Winter or intersession terms appear under the wrong term**: use `sections.season_overrides` to give them their own season.
- **The workbook has blank formula cells**: recalculate in your spreadsheet program.
