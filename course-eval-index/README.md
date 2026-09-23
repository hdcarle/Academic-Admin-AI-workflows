# course-eval-index

Turn a folder of course-evaluation reports (PDFs) into a job-market-ready **teaching workbook**:

- **Course Index**: one row per section and term, with course, format (in-person or online), term, UG or GR, students taught, the average rating for each evaluation item, and an **Avg. Overall**.
- **Summary**: live formulas for students taught overall, by format, by level, and by format × level; average ratings by group, course, and year; career average by item.
- **Student Verbatims**: your best student comments, exact wording, tagged by theme, course, term, format, and level.
- **Method & Notes**: definitions and footnotes, so any number can be defended if a search committee asks.

It was built for a teacher looking to summarize their student reach or to generate data for an academic job search, where "I taught 1,100 students across 40 sections, and here is every rating" is stronger than adding a few hand-picked quotes. It works with any evaluation format: a built-in parser handles Campus Labs / Anthology reports, a configurable parser handles other text-table formats, and Claude can write a new parser from one sample report ([docs/ADAPTER_GUIDE.md](docs/ADAPTER_GUIDE.md)).

## What you get

| Sheet | What it does |
| --- | --- |
| Course Index | Course, Format, Term, UG or GR, # taught, one column per evaluation item, Avg. Overall, respondents, response rate, notes, source file. Small samples are highlighted. |
| Summary | Every number is a live Excel formula over Course Index, so editing a row updates the totals. |
| Student Verbatims | Curated quotes from your `verbatims.csv`, checked against the source text so the wording is exact. |
| Method & Notes | How each column was defined, what was excluded from Avg. Overall, and why. |

## Get started

Pick one. Option 1 is easier if you do not code; Option 2 is fully manual.

### Option 1: with Claude (recommended)

You need a Claude app that can read your files and run Python: **Claude Code**, or the **Claude desktop app in Cowork mode** with a folder connected. A browser chat that cannot access your files will not work.

**Step 1. Get the tool.** Download this repository (green **Code** button > **Download ZIP**, then unzip) or clone it. You need the `course-eval-index` folder. Put your evaluation PDFs in a separate folder, for example `course-eval-index/reports/` (`reports/` is git-ignored).

**Step 2. Install the skill.** A skill is a set of instructions Claude follows for this workflow. Use whichever route matches your app. A zip is already provided at `skill/course-eval-index.zip`, so you do not need to build one.

- *Claude desktop app or claude.ai (no terminal):*
  1. On this repository page, open the `skill` folder, click `course-eval-index.zip`, and download it (or use the copy from Step 1's download). Do not unzip it.
  2. In Claude, open **Settings**, then **Skills** (it may sit under Capabilities or Customize).
  3. Choose **Upload skill** (or **Add skill**) and select the zip.
  4. Turn the skill on, then start a new chat.
- *Claude Code (terminal):* copy the folder into your skills directory, then start a new Claude Code session.

  ```bash
  mkdir -p ~/.claude/skills
  cp -r skill/course-eval-index ~/.claude/skills/
  ```

  On Windows, copy it to `%USERPROFILE%\.claude\skills\`.

If your Settings has no Skills page, skip this step and use the **No skill?** prompt below.

**Step 3. Point Claude at your files.** Claude Code: open a terminal in the `course-eval-index` folder and run `claude`. Cowork: connect the `course-eval-index` folder, and connect the folder with your PDFs if it is elsewhere.

**Step 4. Paste this prompt** (first time only):

> Set up course-eval-index for my course evaluations. The tool is in this folder, and my evaluation PDFs are in `reports/`. Follow the course-eval-index skill. Look at one of my reports, then ask me the three rules (how to tell a section is online, where graduate level starts, what a course code looks like). Propose my list of evaluation questions and which of them count toward Avg. Overall, and let me confirm before building. Then build my workbook and check the section and student totals with me.

**Step 5. Answer Claude's questions.** Expect 30 to 60 minutes the first time. Claude will show you a few decisions (which questions are about teaching versus the institution, how to label your online sections) and ask you to confirm the totals against your own records. It will not invent scores; anything it cannot read gets flagged for you.

**No skill?** You can skip Step 2 and paste this instead: *"Read README.md, SETUP.md, and docs/METHODOLOGY.md in this folder, then do the first-time setup with me, step by step. Ask me before you decide anything about which questions count toward Avg. Overall."*

**Prompts for later** (paste as needed):

- *New semester:* "I added new evaluation PDFs to `reports/`. Use course-eval-index to rebuild my workbook, walk me through any warnings, and confirm the totals only went up."
- *Student quotes:* "Use course-eval-index to propose 30 to 60 candidate student quotes from my comments, grouped by theme, exactly as written with names removed. Then verify them."
- *Check before sending:* "Compare five random rows of my workbook against their source PDFs and report any difference."

More prompts are in [docs/PROMPTS.md](docs/PROMPTS.md).

### Option 2: by hand

```bash
git clone https://github.com/hdcarle/Academic-Admin-AI-workflows.git
cd Academic-Admin-AI-workflows/course-eval-index
pip install -r requirements.txt

# Try the bundled demo first (four made-up reports, no PDFs needed)
python -m course_eval parse --config examples/config.yaml
python -m course_eval build --config examples/config.yaml
```

Open `examples/demo_output/Teaching_Evaluation_Index.xlsx`, then follow **[SETUP.md](SETUP.md)** to point the tool at your own reports.

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
skill/course-eval-index/   a Claude skill that walks you through setup
skill/course-eval-index.zip  the same skill, ready to upload in Settings
config.example.yaml     annotated configuration template
SETUP.md                step-by-step setup for your own reports
```

## Contributing

Adapters for other institutions' formats are the most useful contribution. Add `course_eval/adapters/<name>.py` with a class `Adapter(cfg)` that has a `parse(text)` method, and include a fictional sample report in `examples/`. See the adapter guide.

## License

MIT. See the [LICENSE](../LICENSE) at the root of this repository.
