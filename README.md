# Academic-Admin-AI-workflows

Practical, reusable AI-assisted workflows for the administrative side of academic work. Each workflow lives in its own folder with a README, a setup guide, and fictional example data, and is designed to work with Claude (Claude Code or Cowork) or by hand.

Nothing in this repository contains real student, course, or institutional data.

## Workflows

| Workflow | What it does | Start here |
| --- | --- | --- |
| **course-eval-index** | Turns a folder of course-evaluation PDFs into a teaching workbook for job applications and tenure files: one row per section and term with course, format, term, UG or GR, students taught, item ratings, Avg. Overall, live summary totals, and verified student quotes. | [course-eval-index/README.md](course-eval-index/README.md) |

More workflows will be added over time.

## How the workflows are organized

```
<workflow-name>/
  README.md      what it does and how it works
  SETUP.md       step-by-step setup for your own data
  docs/          methodology and guides
  examples/      runnable demo with fictional data
  skill/         optional Claude skill that guides setup
```

## Using a workflow with Claude

Copy the workflow's `skill/SKILL.md` into your Claude skills folder, keep the repository where Claude can read it, and ask Claude to set the workflow up for your data.

## Privacy

Reports, comments, and configuration files that contain real data are excluded by each workflow's `.gitignore`. Please keep it that way, and follow your institution's policy on sharing evaluation data.

## License

MIT. See [LICENSE](LICENSE).
