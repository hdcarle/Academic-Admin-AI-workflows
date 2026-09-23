# Claude prompts that pair with this tool

Use these with Claude Code, Claude Cowork, or any Claude chat that can read your files. Replace the folder names.

## 0. Start here

**First-time setup** (with the skill installed, see the README):

> Set up course-eval-index for my course evaluations. The tool is in this folder, and my evaluation PDFs are in `reports/`. Follow the course-eval-index skill. Look at one of my reports, then ask me the three rules (how to tell a section is online, where graduate level starts, what a course code looks like). Propose my list of evaluation questions and which of them count toward Avg. Overall, and let me confirm before building. Then build my workbook and check the section and student totals with me.

**Without the skill:**

> Read README.md, SETUP.md, and docs/METHODOLOGY.md in this folder, then do the first-time setup with me, step by step. Ask me before you decide anything about which questions count toward Avg. Overall.

**Every new semester:**

> I added new evaluation PDFs to `reports/`. Use course-eval-index to rebuild my workbook, walk me through any warnings, and confirm the totals only went up.

## 1. Draft your `items` list

> Read one report from `text/` (BUS 101 Q1 FA23.txt). List every rating question. Sort them into three buckets: (1) teaching behavior, (2) about the institution or its resources, (3) comparisons or unusual scales. Then write the `items` section of `config.yaml` with a unique `key`, a `label`, a lowercase `match` regex, and a `group` for each. Flag any negatively worded question and tell me how you would treat it.

## 2. Find candidate verbatims

> Read every file in `data/comments/` (and any Word or screenshot text in `text/`). Propose 30 to 60 student comments that would help a teaching statement or job application, grouped into five to eight themes such as career impact, care and responsiveness, course design, and graduate teaching. Quote **exactly**, keep typos, and remove student names. Output a CSV with the columns quote, theme, top_pick, course, term, format, level, source_type, source_file. Mark about a quarter as top picks. Prefer specific comments over generic praise.

Then run `python -m course_eval verify` and fix anything it cannot find.

## 3. Constructive feedback memo (for you, not for applications)

> Read the ratings and comments for BUS 101 (my current course) in `data/sections.json` and `data/comments/`. Write a two- to four-page memo on where I can improve. For each priority, give: the evidence (scores by term and two or three exact quotes), why it matters, and three options ordered from least to most effort. Note which patterns recur across terms and which appear only once. Treat any score based on fewer than 25 respondents as directional.

## 4. Check the workbook before you send it

> Open `output/Teaching_Evaluation_Index.xlsx`. Compare five random rows with their source PDFs and report any difference. Recompute Avg. Overall for those rows. Confirm the totals on the Summary sheet against the Course Index rows. List anything that looks off.
