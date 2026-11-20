from pylatex import Figure, MiniPage, NoEscape

from osdagbridge.core.reports.report_utils import _figure


def ch6_drawings(fig_paths):
    """Chapter 6 – Drawings and Visualizations.

    Layout: section heading → figure → small numbered label below.
    No subsection headers. 6.3 and 6.4 are headings only (no figures).

    Figure numbering (auto-incremented by LaTeX):
      6.1  Overall 3D Bridge Superstructure
      6.2  Typical Cross Section
      6.3  Top View
      6.4  3D View of Plate Girders
      6.5  Cross Section of Plate Girder
      6.6  Side View of Girder
      6.7  Cross Bracing Layout
      6.8  Cross Bracing -- Bracing Section
      6.9  Cross Bracing -- Top Chord Section
      6.10 Cross Bracing -- Bottom Chord Section
      6.11 End Diaphragm Layout
      6.12 End Diaphragm -- Bracing Section
      6.13 End Diaphragm -- Top Chord Section
      6.14 End Diaphragm -- Bottom Chord Section
    """

    sup3d  = _figure(fig_paths.get('final_geometry'),   'Overall 3D Bridge Superstructure', label='fig:bridge-3d')
    cs     = _figure(fig_paths.get('cross_section'),     'Typical Cross Section', label='fig:cross-section')
    gtop   = _figure(fig_paths.get('girder_top'),         'Top View', label='fig:top-view')
    g3d    = _figure(fig_paths.get('girder_3d'),          '3D View of Plate Girders', label='fig:girder-3d')
    gxsec  = _figure(fig_paths.get('section_preview'),   'Cross Section of Plate Girder', label='fig:girder-xsec')
    gside  = _figure(fig_paths.get('stiffener_preview'),  'Side View of Girder', label='fig:girder-side')
    cbdia  = _figure(fig_paths.get('cb_diagram'),         'Cross Bracing Layout', label='fig:cb-layout')

    def _sec_cell(path, title, label=None):
        cell = MiniPage(width=NoEscape(r'0.31\textwidth'), pos='t')
        cell.append(NoEscape(r'\centering'))
        if path:
            cell.append(NoEscape(r'\includegraphics[width=\linewidth]{' + path.replace('\\', '/') + '}'))
        else:
            cell.append(NoEscape(r'\fbox{\parbox{0.95\linewidth}{\centering\textit{[ ' + title + r' ]}}}'))
        cell.append(NoEscape(r'\caption{' + title + '}'))
        if label:
            cell.append(NoEscape(r'\label{' + label + '}'))
        return cell

    def _sec_row(*cells):
        fig = Figure(position='H')
        for i, cell in enumerate(cells):
            if i:
                fig.append(NoEscape(r'\hfill'))
            fig.append(cell)
        return fig.dumps()

    # Cross Bracing section views (Figures 6.8, 6.9, 6.10) — 3 columns
    cb_bracing = _sec_cell(
        fig_paths.get('cb_bracing'),
        'Cross Bracing -- Bracing Section',
        'fig:cb-bracing-sec'
    )

    cb_top = _sec_cell(
        fig_paths.get('cb_top_chord'),
        'Cross Bracing -- Top Chord Section',
        'fig:cb-top-chord'
    )

    cb_bottom = _sec_cell(
        fig_paths.get('cb_bottom_chord'),
        'Cross Bracing -- Bottom Chord Section',
        'fig:cb-bottom-chord'
    )
    cb_sections_row = _sec_row(cb_bracing, cb_top, cb_bottom)

    eddia  = _figure(fig_paths.get('ed_diagram'),        'End Diaphragm Layout', label='fig:ed-layout')

    # End Diaphragm section views (Figures 6.12, 6.13, 6.14) — 3 columns
    ed_bracing = _sec_cell(
        fig_paths.get('ed_bracing'),
        'End Diaphragm -- Bracing Section',
        'fig:ed-bracing-sec'
    )

    ed_top = _sec_cell(
        fig_paths.get('ed_top_chord'),
        'End Diaphragm -- Top Chord Section',
        'fig:ed-top-chord'
    )

    ed_bottom = _sec_cell(
        fig_paths.get('ed_bottom_chord'),
        'End Diaphragm -- Bottom Chord Section',
        'fig:ed-bottom-chord'
    )
    ed_sections_row = _sec_row(ed_bracing, ed_top, ed_bottom)

    return (r"""
\chapter{Drawings and Visualizations}
\label{ch:drawings}

This section presents CAD-generated views of the designed bridge and its components. All views are generated automatically by OsdagBridge using pythonOCC.

\section{Bridge Configuration and Layout}
\label{sec:bridge-layout}

"""
            + sup3d + '\n\n'
            + cs + '\n\n'
            + gtop + r"""

\section{Plate Girder --- Detailed Views}
\label{sec:girder-views}

"""
            + g3d + '\n\n'
            + gxsec + '\n\n'
            + gside + r"""

\section{Cross Bracing Detail}
\label{sec:bracing-detail}

"""
            + cbdia + '\n\n'
            + cb_sections_row + r"""
            

\section{End Diaphragm Detail}
\label{sec:diaphragm-detail}

"""
            + eddia + '\n\n'
            + ed_sections_row + r"""

""")
