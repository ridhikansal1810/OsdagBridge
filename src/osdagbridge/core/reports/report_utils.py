import re

from pylatex import Figure, LongTable, NoEscape

from osdagbridge.core.reports import styles as st

from osdagbridge.core.utils.common import (
    KEY_MP_GD_MEMBER_ID,
    KEY_MP_GD_SELECT_GIRDER,
    KEY_MP_GIRDER_DEPTH,
    KEY_TS_NO_OF_GIRDERS
)

def _fit_widths(spec):
    """Scale the cm column widths down so the table fits the text width."""
    widths = [float(w) for w in re.findall(r'\{([\d.]+)cm\}', spec)]
    room = st.TEXT_WIDTH_CM - st.CELL_PAD_CM * len(widths)
    if not widths or sum(widths) <= room:
        return spec
    k = room / sum(widths)
    return re.sub(r'\{([\d.]+)cm\}', lambda m: '{%.2fcm}' % (float(m.group(1)) * k), spec)


def _long_table(spec, caption, header, body, label=None, compact=False):
    """Longtable whose caption and header row repeat on every page.

    compact=True uses the narrower cell padding (\\compacttables) for wide tables.
    """
    # A row followed by \cline belongs to a \multirow group: \\* (plus the
    # \cline patch in the preamble) stops a page break inside the group, so
    # the group label never lands in the footer.
    body = re.sub(r'\\\\(\[[^\]]*\])?(\s*\\cline)', r'\\\\*\1\2', body)
    table = LongTable(NoEscape(_fit_widths(spec)))
    if caption:
        label_tex = (r'\label{' + label + '}') if label else ''
        table.append(NoEscape(r'\caption{\textbf{' + caption + '}}' + label_tex + r'\\'))
    if header:
        table.add_hline()
        table.append(NoEscape(header))
        table.add_hline()
    table.append(NoEscape(r'\endfirsthead'))
    if caption:
        table.append(NoEscape(r'\caption[]{\textbf{' + caption + r'} (continued)}\\'))
    if header:
        table.add_hline()
        table.append(NoEscape(header))
        table.add_hline()
    table.end_table_header()
    table.append(NoEscape(body))
    if compact:
        return r'\begingroup\compacttables' + '\n' + table.dumps() + '\n' + r'\endgroup'
    return table.dumps()


def _tex(value):
    """Escape a Python value for safe LaTeX embedding."""
    s = str(value) if value is not None else ''
    if not s:
        return r''
    # Normalise non-ASCII glyphs from section designations (e.g. "∠ 100 ⅹ 100ⅹ 10")
    # that pdflatex cannot render.
    for uni, ascii_ in [('∠', 'L'), ('ⅹ', 'x'), ('×', 'x')]:
        s = s.replace(uni, ascii_)
    s = s.replace('\\', r'\textbackslash{}')
    for ch, esc in [('&', r'\&'), ('%', r'\%'), ('$', r'\$'), ('#', r'\#'),
                    ('{', r'\{'), ('}', r'\}'),          
                    ('_', r'\_\allowbreak{}'),            
                    ('~', r'\textasciitilde{}'), ('^', r'\^{}')]:
        s = s.replace(ch, esc)
    s = s.replace(':', r':\allowbreak{}')
    return s


def _render_value(source_dict, key, unit=""):
    val = source_dict.get(key)
    if val in ("", None):
        return ""
    return _tex(val) + unit


def get_girder_entries(input_dict):
    """
    Retrieve all girder labels and member IDs from backend keys.

    Usage Example:
    --------------------------
    girder_entries = get_girder_entries(bridge.input_dict)
    
    # 1. Fallback handling (if backend hasn't populated keys yet)
    if not girder_entries:
        n = int(bridge.input_dict.get(KEY_TS_NO_OF_GIRDERS, 1))
        girder_entries = [(f"Girder {i}", f"M1") for i in range(1, n + 1)]
        
    # 2. Get total number of girders safely
    n_girders = len(girder_entries)
    
    # 3. Iterate over the girders to build table rows
    for lbl, mid in girder_entries:
        # lbl will be e.g., "G1", mid will be e.g., "G1M1"
        # Access girder specific keys dynamically:
        # val = input_dict.get(f"{KEY_MP_GIRDER_DEPTH}.{lbl}.{mid}")
        pass

    Returns:
        List[Tuple[str, str]]
    """
    n = int(input_dict.get(KEY_TS_NO_OF_GIRDERS, 0))

    entries = []

    for i in range(1, n + 1):
        entries.append(
            (
                input_dict.get(f"{KEY_MP_GD_SELECT_GIRDER}.G{i}", ""),
                input_dict.get(f"{KEY_MP_GD_MEMBER_ID}.G{i}.M1", ""),
            )
        )

    return entries


def _figure(path, caption, width=st.FIGURE_WIDTH, numbered=True, label=None):
    """Figure with the image, or a placeholder box when there is no image."""
    fig = Figure(position='H')
    if path:
        fig.add_image(path.replace('\\', '/'), width=NoEscape(width))
    else:
        fig.append(NoEscape(r'\centering\fbox{\parbox{0.97\textwidth}{\textit{[ PLACEHOLDER: '
                            + caption + r' ]}}}'))
    if numbered:
        fig.add_caption(NoEscape(caption))
    else:
        fig.append(NoEscape(r'\caption*{' + caption + '}'))
    if label:
        fig.append(NoEscape(r'\label{' + label + '}'))
    return fig.dumps()
