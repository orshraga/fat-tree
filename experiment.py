"""
Failure-rate sweep: for each k and failure rate, run many seeds, record the
fraction of reachable host pairs, write CSV files, and plot the summary.

Usage:
  python experiment.py --config configs/sweep.json
"""

import argparse
import csv
import json
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # render to files; no window needed
import matplotlib.pyplot as plt  # noqa: E402

from failures import inject_failures  # noqa: E402
from fattree import build_fat_tree  # noqa: E402
from metrics import reachable_host_pairs  # noqa: E402


def run_sweep(k_values, rates, seeds):
    """One row per (k, rate, seed)."""
    rows = []
    for k in k_values:
        healthy = build_fat_tree(k)
        for rate in rates:
            for seed in seeds:
                damaged, _ = inject_failures(healthy, rate, seed)
                good, total = reachable_host_pairs(damaged)
                rows.append({
                    "k": k,
                    "failure_rate": rate,
                    "seed": seed,
                    "reachable_fraction": good / total,
                })
    return rows


def summarize(rows):
    """Mean and sample standard deviation per (k, rate)."""
    groups = {}
    for r in rows:
        groups.setdefault((r["k"], r["failure_rate"]), []).append(r["reachable_fraction"])

    summary = []
    for (k, rate), values in sorted(groups.items()):
        summary.append({
            "k": k,
            "failure_rate": rate,
            "mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0.0,
            "runs": len(values),
        })
    return summary


def write_csv(path: Path, rows: list) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_summary(summary, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for k in sorted({s["k"] for s in summary}):
        points = [s for s in summary if s["k"] == k]
        ax.errorbar(
            [p["failure_rate"] * 100 for p in points],
            [p["mean"] for p in points],
            yerr=[p["std"] for p in points],
            marker="o", capsize=3, label=f"k = {k}",
        )
    ax.set_xlabel("Fabric link failure rate (%)")
    ax.set_ylabel("Reachable host pairs (fraction)")
    ax.set_title("Connectivity under switch-to-switch link failures")
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Failure-rate sweep and plot.")
    parser.add_argument("--config", required=True, help="JSON config, see configs/sweep.json")
    args = parser.parse_args(argv)

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)

    k_values = cfg["k_values"]
    rates = cfg["failure_rates"]
    seeds = range(cfg.get("num_seeds", 30))
    out_dir = Path(cfg.get("out_dir", "results"))
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = run_sweep(k_values, rates, seeds)
    summary = summarize(rows)

    write_csv(out_dir / "reachability_raw.csv", rows)
    write_csv(out_dir / "reachability_summary.csv", summary)
    plot_summary(summary, out_dir / "reachability_vs_failure.png")

    print(f"{'k':>3} {'rate':>6} {'mean':>8} {'std':>8} {'runs':>5}")
    for s in summary:
        print(f"{s['k']:>3} {s['failure_rate']:>6.2f} {s['mean']:>8.4f} {s['std']:>8.4f} {s['runs']:>5}")
    print(f"\nwrote {out_dir}/reachability_summary.csv, reachability_raw.csv, reachability_vs_failure.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
