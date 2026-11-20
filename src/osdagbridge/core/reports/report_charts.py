# =============================================================================
# Bar charts embedded in the design report (saved as PNG, then \includegraphics)
# Uses matplotlib.figure.Figure directly so the GUI's pyplot backend is untouched.
# =============================================================================
import os

from matplotlib.figure import Figure

PASS_COLOR = "#91B014"
FAIL_COLOR = "#D62728"
BAR_COLOR = "#4C72B0"
CONCRETE_COLOR = "#8C8C8C"
REBAR_COLOR = "#B5651D"


def _save(fig, img_dir, name):
    fig.tight_layout()
    path = os.path.join(img_dir, name + ".png")
    fig.savefig(path, dpi=150)
    return path.replace("\\", "/")


def _bars(ax, labels, values, ylabel, color):
    bars = ax.bar(labels, values, color=color, width=0.5)
    ax.bar_label(bars, fmt="%.2f", fontsize=8)
    ax.set_xlim(-0.75, len(labels) - 0.25)
    ax.set_ylim(0, max(values) * 1.2 or 1)
    ax.set_ylabel(ylabel)


def ur_chart(img_dir, name, title, labels, urs):
    """Utilization ratio bars with the UR = 1.0 limit as a red dashed line."""
    fig = Figure(figsize=(6.5, 3.2))
    ax = fig.subplots()
    bars = ax.bar(labels, urs, color=[PASS_COLOR if u <= 1.0 else FAIL_COLOR for u in urs])
    ax.bar_label(bars, fmt="%.2f", fontsize=8)
    ax.axhline(1.0, color="red", linestyle="--", linewidth=1.2, label="UR = 1.0")
    ax.set_ylim(0, max(1.3, max(urs) * 1.25))
    ax.set_ylabel("Utilization Ratio")
    ax.set_title(title, fontsize=10)
    ax.legend(loc="best", fontsize=8)
    ax.tick_params(axis="x", labelsize=8, labelrotation=20)
    for tick in ax.get_xticklabels():
        tick.set_ha("right")
    return _save(fig, img_dir, name)


def steel_chart(img_dir, labels, tonnes):
    """Structural steel tonnage per member type."""
    fig = Figure(figsize=(6.5, 3.0))
    ax = fig.subplots()
    _bars(ax, labels, tonnes, "Weight (MT)", BAR_COLOR)
    ax.set_title("Structural Steel", fontsize=10)
    return _save(fig, img_dir, "qty_steel")


def concrete_rebar_chart(img_dir, concrete_m3, rebar_t):
    """Deck concrete volume and reinforcement weight, each on its own axis."""
    fig = Figure(figsize=(6.5, 3.0))
    ax1, ax2 = fig.subplots(1, 2)
    _bars(ax1, ["Deck Concrete"], [concrete_m3], "Volume (m$^3$)", CONCRETE_COLOR)
    _bars(ax2, ["Reinforcement Steel"], [rebar_t], "Weight (MT)", REBAR_COLOR)
    ax1.set_title("Concrete", fontsize=10)
    ax2.set_title("Reinforcement", fontsize=10)
    return _save(fig, img_dir, "qty_concrete_rebar")
