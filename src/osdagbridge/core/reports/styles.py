# =============================================================================
# Report styles — single source of truth for the design report's look.
# preamble() in report_generator.py turns these into LaTeX settings, lengths
# (\rowsep), commands (\compacttables) and colours (osdagGreen, fail); chapter
# files use those LaTeX names, and Python code imports the values below.
# =============================================================================

# Page layout
FONT_SIZE = "12pt"
PAPER = "a4paper"
MARGIN = "1in"
HEAD_HEIGHT = "18pt"
LINE_SPREAD = "1.15"
TEXT_WIDTH_CM = 15.9          # A4 width minus 2 x MARGIN

# Colours (HTML hex)
BRAND_COLOR = "91B014"        # Osdag green: header/footer rules, passing bars
FAIL_COLOR = "D62728"         # failing values in tables and charts
BAR_COLOR = "4C72B0"
CONCRETE_COLOR = "8C8C8C"
REBAR_COLOR = "B5651D"

# Header / footer
FOOTER_TEXT = r"Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay"
HF_RULE_WIDTH = "1pt"

# Tables
TABCOLSEP = "6pt"             # cell padding
TABCOLSEP_COMPACT = "4pt"     # \compacttables, for wide tables
CELL_PAD_CM = 0.45            # 2 x TABCOLSEP + rule, used to fit column widths
ARRAY_STRETCH = "1.12"
ROW_SEP = "6pt"               # \rowsep, extra space after each body row
TABLE_RULE_WIDTH = "0.5pt"
EXTRA_ROW_HEIGHT = "0.6pt"
TABLE_SPACE_BEFORE = "1em"    # \LTpre
TABLE_SPACE_AFTER = "6pt"     # \LTpost
CAPTION_SKIP = "2pt"

# Figures and charts
FIGURE_WIDTH = r"0.85\textwidth"
CHART_WIDTH = r"0.8\textwidth"
CHART_SIZE = (6.5, 3.2)       # inches
CHART_DPI = 150
CHART_FONT_SIZE = 8
CHART_TITLE_SIZE = 10
