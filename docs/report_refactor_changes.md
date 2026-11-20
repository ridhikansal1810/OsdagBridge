# Report Generator Refactoring — Technical Changes

Branch: `report-refactor` (off `dev`). One commit per scope item.

All changes are under `src/osdagbridge/core/reports/`, plus `pylatex` added to
`pyproject.toml` and `requirements.txt` (it was only installed indirectly via the
`osdag` package before).

## Files changed

| File | Change |
|---|---|
| `report_utils.py` | `_long_table` (PyLaTeX `LongTable` with repeating caption/header, width fitting, multirow keep-together, `compact` option) and `_figure` (PyLaTeX `Figure`). Replaces `_fig_or_placeholder` / `_fig_embed`. |
| `styles.py` | **New.** Single source of truth for all formatting values. |
| `report_charts.py` | **New.** Matplotlib bar charts: utilization ratio, steel tonnage, concrete vs reinforcement. |
| `report_generator.py` | Preamble built from `styles.py`; `\cline` patch; `headheight`; removed the `needspace` hook on longtable; passes the image folder to Chapters 5 and 7. |
| `chap1.py`, `chap2.py`, `chap4.py`, `chap8.py`, `executive_summary.py` | All tables (incl. former `table`/`tabular` blocks) via `_long_table`; local spacing/padding overrides removed. |
| `chap3.py` | Live loads split into a per-vehicle table and a footpath table. |
| `chap5.py` | Tables via `_long_table`; Section 5.5 UR charts built from Table 5.22 rows. |
| `chap6.py` | Figures via PyLaTeX `Figure`; three-up section views are a `Figure` of `MiniPage`s. |
| `chap7.py` | Bill of materials via `_long_table`; steel tonnage and concrete/rebar charts. |

## 1. Repeated table headers

`_long_table(spec, caption, header, body, label=None, compact=False)` builds a
PyLaTeX `LongTable`: caption + header row, `\endfirsthead`, the same header with
"(continued)" caption, `\endhead`, then the body. Every chapter table goes
through it, so every page break repeats the column headers.

Row bodies are still built as LaTeX row strings (the existing row builders are
unchanged) and appended as `NoEscape`; only the table environment, caption and
header handling moved to PyLaTeX. Custom column types `L{}`/`C{}` are not
understood by PyLaTeX's column counter, so rows are appended as raw content.

The preamble used to run `\needspace{5\baselineskip}` before every longtable.
That fought longtable's own "does the first row fit?" check and printed the
continued header *above* the first header on 9 tables, so the hook was removed
for longtable (longtable already does this check itself).

Longtable captions now end with `\\` (longtable treats `\caption` as a row);
this removes an "Extra alignment tab" LaTeX error that every table produced.

## 2. Layout and footer overlap

* **Rows in the footer (e.g. "G4" on page 30):** a girder's rows form a
  `\multirow` group. When a page broke inside the group, the label was centred
  over rows on the next page and printed in the footer. Rows followed by
  `\cline` now end with `\\*`, and `\@cline` is patched (etoolbox) to put
  `\nobreak` before its negative skip — otherwise the break just moves below the
  rule. Groups now always stay on one page.
* `headheight` set to 18 pt (fancyhdr warned 12 pt was too small).
* Tables wider than the text (up to ~2 cm into the right margin): `_long_table`
  scales the `cm` column widths down proportionally when widths + padding exceed
  the text width.
* Table 4.1 had a 3-line label in a 2-row `\multirow` (overfull vbox) — now 2 lines.
* `\emergencystretch` added so lines with long inline maths wrap.

## 3. Live loads (Chapter 3)

**Table 3.3 Vehicle Live Loads** — one row per vehicle selected in the loading
tab, following the layout in the task document:

| Vehicle | Total Load (kN) | Impact Factor | Braking: Considered? | Value (kN) | Eccentricity (m) |

* Total load: from the IRC 6 vehicle functions (Class A, 70R Wheeled, SV,
  Fatigue); vehicles without a function use their IRC 6 gross weight × g
  (70R Tracked / AA Tracked 70 t, 70R Bogie / AA Wheeled 40 t). Custom vehicles
  use the sum of their axle loads.
* Impact factor: 1 + IM from IRC 6 Cl. 208.2 (Class A) / 208.3 (AA, 70R);
  custom vehicles use their stored impact factor; SV and Fatigue show "---".
* Braking: considered for all selected vehicles except Fatigue; Class SV follows
  the "Braking Load → Class SV" checkbox. Value = 20 % of the vehicle load
  (IRC 6 Cl. 211.2). Eccentricity = the loading-tab input (default 1.2 m).

**Table 3.4 Footpath Live Load** — value, unit and basis (IRC 6 Cl. 206.1,
user-defined, or "not applicable" when the bridge has no footpath).

## 4. Utilization ratio charts (Section 5.5)

Table 5.22's rows are now kept as `(element, label, cells)` tuples, so the
table and the charts use the same numbers. One chart per element (plate
girders, deck slab, cross bracing, end diaphragms), with a red dashed
`UR = 1.0` line and failing bars in red. Elements without numeric URs are
skipped (e.g. rolled/welded end diaphragms, whose design is not implemented).

## 5. Material quantity charts (Chapter 7)

After Table 7.1: structural steel tonnage (girders vs total cross bracing) and
deck concrete volume (m³) next to reinforcement weight (MT) on separate axes.
End diaphragm quantities are not computed by the BOQ module, so they are not
charted.

Charts use `matplotlib.figure.Figure` directly (not `pyplot`) so the desktop
app's Qt plotting backend is untouched. PNGs are written to the report's
temporary image folder and embedded with a PyLaTeX `Figure`.

## 6. Centralized formatting — `styles.py`

```
Page layout     FONT_SIZE, PAPER, MARGIN, HEAD_HEIGHT, LINE_SPREAD, TEXT_WIDTH_CM
Colours         BRAND_COLOR, FAIL_COLOR, BAR_COLOR, CONCRETE_COLOR, REBAR_COLOR
Header/footer   FOOTER_TEXT, HF_RULE_WIDTH
Tables          TABCOLSEP, TABCOLSEP_COMPACT, CELL_PAD_CM, ARRAY_STRETCH, ROW_SEP,
                TABLE_RULE_WIDTH, EXTRA_ROW_HEIGHT, TABLE_SPACE_BEFORE,
                TABLE_SPACE_AFTER, CAPTION_SKIP
Figures/charts  FIGURE_WIDTH, CHART_WIDTH, CHART_SIZE, CHART_DPI,
                CHART_FONT_SIZE, CHART_TITLE_SIZE
```

How it is consumed:

* `preamble()` builds the LaTeX settings from these values and defines
  `\rowsep` (row spacing), `\compacttables` (narrow padding) and the `fail`
  colour. Chapter row strings use `\\[\rowsep]` and `\textcolor{fail}`.
* Python code imports the values (`report_utils`, `report_charts`, chapter
  figure widths).

Removed from chapter files: hardcoded `[6pt]`/`[8pt]` row spacing, local
`\tabcolsep` (now `compact=True`), `\LTleft`/`\LTright` and caption-skip
overrides (these leaked into every later chapter), per-table `\vspace` (now
`\LTpre`), and the two duplicated header/footer blocks (now one definition).

Per-table column widths stay next to their tables; they describe content, not
style.

## Rationale

* **Raw LaTeX rows inside PyLaTeX tables:** converting ~1,500 lines of row
  builders to PyLaTeX cell objects would rewrite the business logic around
  them; wrapping them keeps the diff reviewable while table structure,
  headers and figures go through PyLaTeX.
* **LaTeX lengths/commands for chapter strings:** `\\[\rowsep]` keeps hundreds
  of row strings readable while the value still comes from `styles.py`.

## Known issues (not changed)

* `IRC6_2017.cl_208_3_impact_factor` tests the global `KEY_VEHICLE` list, which
  is always truthy, so it always takes the 70R tracked branch.
* `IRC6_2017.cl_211_2_braking_force` fails for 1–2 lanes (`braking_force_2`
  unbound) and mixes N with tonnes; the report no longer uses it.
* A check name containing `≤` (executive summary) is not rendered by pdflatex.
* Cross bracing and end diaphragm values depend on `osdag_core`, which the
  `osdag` 2025.01 package in `environment.yml` does not provide.
