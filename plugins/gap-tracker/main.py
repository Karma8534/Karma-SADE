"""gap-tracker plugin — queries preclaw1 gap map for Nexus progress."""
import sys
from pathlib import Path

# Add Scripts/ to path for gap_map import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "Scripts"))
from gap_map import parse_gap_map


def gap_status():
    """Returns current gap map totals."""
    _, features, categories = parse_gap_map()
    totals = {"HAVE": 0, "PARTIAL": 0, "MISSING": 0, "N/A": 0}
    for cat_counts in categories.values():
        for s in totals:
            totals[s] += cat_counts.get(s, 0)
    return {
        "totals": totals,
        "total_features": len(features),
        "completion_pct": round(totals["HAVE"] / max(1, len(features)) * 100, 1),
    }


def gap_missing():
    """Returns list of MISSING features."""
    _, features, _ = parse_gap_map()
    return [
        {"feature": f["feature"], "category": f["category"]}
        for f in features if f["status"] == "MISSING"
    ]


# Plugin tool registry — PluginManager reads this
TOOLS = {
    "gap_status": gap_status,
    "gap_missing": gap_missing,
}
