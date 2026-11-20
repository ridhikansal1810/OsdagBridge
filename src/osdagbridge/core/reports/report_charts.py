# Bar charts for the design report. Uses matplotlib.figure.Figure, not pyplot,
# so the GUI's plotting backend is not touched.
import os

from matplotlib.figure import Figure

from osdagbridge.core.reports import styles as st


def _save(fig, img_dir, name):
    fig.tight_layout()
    path = os.path.join(img_dir, name + ".png")
    fig.savefig(path, dpi=st.CHART_DPI)
    return path.replace("\\", "/")


def _bars(ax, labels, values, ylabel, color):
    bars = ax.bar(labels, values, color=color, width=0.5)
    ax.bar_label(bars, fmt="%.2f", fontsize=st.CHART_FONT_SIZE)
    ax.set_xlim(-0.75, len(labels) - 0.25)
    ax.set_ylim(0, max(values) * 1.2 or 1)
    ax.set_ylabel(ylabel)


def ur_chart(img_dir, name, title, labels, urs):
    fig = Figure(figsize=st.CHART_SIZE)
    ax = fig.subplots()
    bars = ax.bar(labels, urs, color=["#" + (st.BRAND_COLOR if u <= 1.0 else st.FAIL_COLOR) for u in urs])
    ax.bar_label(bars, fmt="%.2f", fontsize=st.CHART_FONT_SIZE)
    ax.axhline(1.0, color="red", linestyle="--", linewidth=1.2, label="UR = 1.0")
    ax.set_ylim(0, max(1.3, max(urs) * 1.25))
    ax.set_ylabel("Utilization Ratio")
    ax.set_title(title, fontsize=st.CHART_TITLE_SIZE)
    ax.legend(loc="best", fontsize=st.CHART_FONT_SIZE)
    ax.tick_params(axis="x", labelsize=st.CHART_FONT_SIZE, labelrotation=20)
    for tick in ax.get_xticklabels():
        tick.set_ha("right")
    return _save(fig, img_dir, name)


def steel_chart(img_dir, labels, tonnes):
    fig = Figure(figsize=st.CHART_SIZE)
    ax = fig.subplots()
    _bars(ax, labels, tonnes, "Weight (MT)", "#" + st.BAR_COLOR)
    ax.set_title("Structural Steel", fontsize=st.CHART_TITLE_SIZE)
    return _save(fig, img_dir, "qty_steel")


def concrete_rebar_chart(img_dir, concrete_m3, rebar_t):
    fig = Figure(figsize=st.CHART_SIZE)
    ax1, ax2 = fig.subplots(1, 2)
    _bars(ax1, ["Deck Concrete"], [concrete_m3], "Volume (m$^3$)", "#" + st.CONCRETE_COLOR)
    _bars(ax2, ["Reinforcement Steel"], [rebar_t], "Weight (MT)", "#" + st.REBAR_COLOR)
    ax1.set_title("Concrete", fontsize=st.CHART_TITLE_SIZE)
    ax2.set_title("Reinforcement", fontsize=st.CHART_TITLE_SIZE)
    return _save(fig, img_dir, "qty_concrete_rebar")
