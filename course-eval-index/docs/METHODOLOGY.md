# Methodology and defensibility

If a search committee asks "how did you get this number?", every answer should be traceable to a printed score. This page explains the choices and how to defend them.

## Avg. Overall

Most evaluation systems print item means but no composite. **Avg. Overall = the simple (unweighted) average of the item means in the groups you flag `in_avg_overall`.**

Why simple and unweighted:

- It is reproducible from the row: add up the visible item columns and divide.
- Each item counts once, so a question with more responses does not dominate.
- It cannot be tuned. Any composite that weights items invites the question "why those weights?"

Summary lines (by course, by year, career) are **respondent-weighted**: each section's Avg. Overall counts in proportion to how many students responded, so a two-person section cannot swing an average.

If asked for an exact evaluation: hand over the PDF. The workbook's Source file column names it, and every value in the row is a printed mean.

## Which questions belong in Avg. Overall

Sort every question into one of three buckets before you flag anything:

1. **Teaching behavior** (include): "The instructor treated students with respect", "gave feedback in a timely manner", "explained material clearly".
2. **Not about you** (separate group): questions about the institution or its resources ("The library resources were easy to access", "technical support is stated clearly", "accessibility policies are stated"), and required program-level statements. These say little about your teaching and can pull an average down for reasons you do not control. Keep them as visible columns for transparency.
3. **Comparisons and unusual scales** (separate group): "I learned more than in other classes at this school", "this professor was among the best I have had", and letter-grade items. They compare across a pool you cannot see, and their scales may differ.

Two judgment calls:

- **Rigor items** ("This course challenged me", "The workload was challenging") can be read as strength (rigor) or weakness (overload) depending on the reader. Including them as printed is defensible. Say so in `method_notes`.
- **Negatively worded items** ("I was confused about what was expected") should be **reverse-scored** or kept out. To reverse-score, add `reverse: true` to the item in `config.yaml` (the tool flips the printed mean, so 2.0 becomes 4.0 on a 5-point scale) and leave it out of `top_box_groups`. Record what you did in `method_notes`.

## Small samples

Sections with only a few respondents are **flagged, not dropped**. You taught the section, and dropping it under-reports your teaching load. Weighting by respondents keeps them from distorting averages. Set `min_respondents` if you want to exclude them from the averages, and keep them in the counts either way.

## Students taught

`# taught` is **enrollment on the report**, not the number of respondents. For combined reports (for example an honors and a regular section on one report), use the combined enrollment, and the workbook notes it.

## Format and level

- **Format** comes from a pattern in the section code (`online_code_regex`). Verify the pattern with your registrar's convention. For combined sections, the tool treats the report as online if any listed code matches.
- **Level** comes from the course number (`graduate_min_course_number`). Check any course near the line.

## Survey changes over time

Institutions revise their forms. Define each form under `surveys` with its own items. Rows from different forms are never mixed inside one Avg. Overall unless a group is flagged `in_avg_overall` for both, and you can restrict summary averages to a single form (`summary.avg_overall_survey`). Sections and students are counted across all forms.

## Recomputed means

Some reports print counts only. The tool recomputes the mean from the counts and checks the method against every report that prints both. Any mismatch becomes a warning. Values you type by hand (`item_values` in `overrides.yaml`) should be listed in `method_notes`.

## Honest presentation

The tool helps you organize and present accurate numbers. It does not select, adjust, or invent scores. Include the terms that are less flattering, because a full record of every section is more credible than a curated one, and the small-sample and note columns give context where it is needed.
