# =============================================================================
# Bar charts embedded in the design report (saved as PNG, then \includegraphics)
# Uses matplotlib.figure.Figure directly so the GUI's pyplot backend is untouched.
# =============================================================================
import os

from matplotlib.figure import Figure

PASS_COLOR = "#91B014"
FAIL_COLOR = "#D62728"
BAR_COLOR = "#4C72B0"


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
    fig.tight_layout()
    path = os.path.join(img_dir, name + ".png")
    fig.savefig(path, dpi=150)
    return path.replace("\\", "/")
