# Report sources

`../Library-Management-System-Report.pdf` is built from these files. Nothing here
is needed to run the application — it is the toolchain that produced the report,
kept so the figures can be regenerated rather than trusted.

```bash
python3 -m venv .venv && .venv/bin/pip install reportlab matplotlib pillow

.venv/bin/python docs/report/collect.py      # re-run the harness, write data.json
.venv/bin/python docs/report/charts.py       # figures 4, 9, 10 (measured data)
.venv/bin/python docs/report/diagrams1.py    # figures 1, 2
.venv/bin/python docs/report/diagrams2.py    # figures 3, 5, 6
.venv/bin/python docs/report/diagrams3.py    # figures 7, 8
.venv/bin/python docs/report/build.py docs/Library-Management-System-Report.pdf
```

Run them from the project root; `collect.py` imports the stress harness from
`tests/stress/` and re-measures everything the report quotes. The rendered figures
land in `docs/report/figs/` and are gitignored — they are derived artefacts, so the
PDF and these scripts are what the repository keeps.

| File | Role |
|---|---|
| `collect.py` | Runs the fuzz, both concurrency experiments and the static analyses; writes `data.json` |
| `data.json` | The measurements the report quotes — regenerated, never hand-edited |
| `style.py` | Shared chart style (palette, typography, print surface) |
| `draw.py` | Small toolkit for the schematic figures |
| `charts.py` | Data-driven figures: fine accrual, fuzz outcomes, the race before and after |
| `diagrams1-3.py` | Schematics: architecture, ER model, loan lifecycle, sequences, password migration, coverage map |
| `build.py` | Assembles the PDF (reportlab): page template, table of contents, tables, figures |

The palette follows the data-visualisation reference palette: categorical hues in
fixed order, status colours reserved for good and critical, and a white print surface.
