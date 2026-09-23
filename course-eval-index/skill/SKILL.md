---
name: course-eval-index
description: Set up and run the course-eval-index tool that turns a professor's course-evaluation PDFs into a teaching workbook (course, format, term, UG or GR, students taught, item ratings, Avg. Overall, verbatims). Use when the user wants to index course evaluations, prepare teaching evidence for job applications or tenure files, or add a new semester's evaluations.
---

# course-eval-index

This skill walks a professor through turning course-evaluation reports into a defensible teaching workbook using the `course_eval` Python tool in this repository. Read `README.md`, `SETUP.md`, `docs/ADAPTER_GUIDE.md`, and `docs/METHODOLOGY.md` first if you have not.

To install as a Claude skill: copy this folder into your skills directory as `course-eval-index/SKILL.md` (Claude Code: `~/.claude/skills/`), and keep the repository somewhere Claude can read it.

## First-time setup

1. **Find the repo and the reports.** Ask where the repository and the evaluation PDFs are. Confirm Python, `pdftotext`, and `openpyxl` and `PyYAML` are installed (`pip install -r requirements.txt`). Tesseract is only needed for scanned PDFs.
2. **Ask the three rules** in one message (use a multiple-choice question if available):
   - How can you tell a section is online? (for example, a `D` in the section code)
   - At what course number does graduate level start? (default 500)
   - What does a course code look like? (for example `BUS 101`)
3. **Look at one report.** Run `python -m course_eval extract`, open one file in `text/`, and decide the adapter: `anthology_campuslabs`, `regex_table`, or a new adapter (see the adapter guide; write one from a sample if needed and test it on the sample).
4. **Build the items list.** List every rating question. Sort each into teaching behavior, institution/resource-focused, or comparison/unusual scale (see METHODOLOGY.md). Propose the `items` and `groups` and flag negatively worded questions. **Ask the user to confirm which groups feed Avg. Overall before building.**
5. **Write `config.yaml`** from `config.example.yaml`. Run `parse`, then work through `data/warnings.txt` line by line with the user (fix regexes, add `overrides.yaml` entries, OCR garbled PDFs with `--force-ocr` and read the result by eye).
6. **Check totals with the user** (sections, students, in-person vs online, UG vs GR) against their own records before building.
7. **Build**, recalculate the workbook if your viewer shows empty formula cells, and spot-check five rows against the PDFs.
8. **Verbatims.** Read `data/comments/` and other comment files, propose candidates by theme in `verbatims.csv` format (exact wording, names removed), then run `verify` and fix anything not found.

## Each later semester

Put new PDFs in the reports folder and run `python -m course_eval run`. Read `data/warnings.txt`. Add any new `overrides.yaml` entries or `items`. Rebuild, add new quotes, and run `verify`. Do not change existing config unless the survey form changed; then add a new `surveys` entry and items rather than editing old ones.

## Rules

- Never invent or adjust scores. Values typed by hand go in `overrides.yaml` `item_values` and must be listed in `method_notes`.
- Count every section you have a report for. Flag small samples; do not drop them unless the user asks.
- Never commit real reports, comments, `config.yaml`, `overrides.yaml`, `verbatims.csv`, or the workbook to a public repository.
- Quote students exactly, including typos. Remove names. Do not paraphrase inside quotation marks.
- If the user shares the workbook with anyone, remind them to check their institution's policy on evaluation data.
- Keep responses short and directive. Offer two or three options when there is a real choice.
