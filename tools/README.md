# tools/

## manpower_schedule.py — Manpower-Loaded Schedule generator

Generates an `.xlsx` weekly manpower-loaded schedule (the construction "crew curve"
artifact) from a list of activities. This is the engine behind the **Manpower schedule**
skill shown in the cockpit, and supports the "Level 3 buildout" work task.

```bash
pip install openpyxl

# built-in sample -> tools/output/manpower_schedule.xlsx
python manpower_schedule.py

# from your own plan
python manpower_schedule.py --in sample_plan.json --out output/beta.xlsx

# override hours/week
python manpower_schedule.py --hours-per-week 50
```

**Output workbook**
- *Manpower Schedule* sheet — activities × weeks grid, crew loaded per week with a
  trade color spine, a TOTAL MANPOWER row, per-activity man-hours, and a summary block
  (peak manpower, total man-hours, avg crew, duration).
- *Crew Curve* sheet — a manpower histogram chart driven by the weekly totals.

**Load curves** per activity: `flat`, `ramp` (triangular peak), `front` (front-loaded),
`back` (back-loaded).

See `sample_plan.json` for the input format.
