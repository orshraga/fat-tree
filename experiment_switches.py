"""
Experiment 2: switches that lose two or more links, at a fixed failure rate,
as a function of the switch port count k.

Usage:
  python experiment_switches.py --config configs/switches_1pct.json
"""

import argparse
import csv
import json
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # render to files; no window needed
import matplotlib.pyplot as plt  # noqa: E402

from failures import fabric_links, sample_failures  # noqa: E402
from fattree import build_fat_tree, describe  # noqa: E402
from metrics import switches_with_multiple_failures  # noqa: E402


def run(k_values, rate, seeds):
    """One row per (k, seed)."""
    rows = []
    for k in k_values:
        g = build_fat_tree(k)
        links = fabric_links(g)
        counts = describe(g)
        n_switches = counts["edge"] + counts["agg"] + counts["core"]
        for seed in seeds:
            failed = sample_failures(links, rate, seed)
            multi = switches_with_multiple_failures(failed)
            rows.append({
                "k": k,
                "failure_rate": rate,
                "seed": seed,
                "failed_links": len(failed),
                "total_switches": n_switches,
                "multi_fail_switches": multi,
                "fraction": multi / n_switches,
            })
    return rows


def summarize(rows):
    """Mean and sample standard deviation per k."""
    groups = {}
    for r in rows:
        groups.setdefault(r["k"], []).append(r)

    summary = []
    for k, rs in sorted(groups.items()):
        counts = [r["multi_fail_switches"] for r in rs]
        fracs = [r["fraction"] for r in rs]
        summary.append({
            "k": k,
            "failed_links": rs[0]["failed_links"],
            "total_switches": rs[0]["total_switches"],
            "mean_count": statistics.mean(counts),
            "std_count": statistics.stdev(counts) if len(counts) > 1 else 0.0,
            "mean_fraction": statistics.mean(fracs),
            "std_fraction": statistics.stdev(fracs) if len(fracs) > 1 else 0.0,
            "runs": len(rs),
        })
    return summary


def write_csv(path: Path, rows: list) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_summary(summary, path: Path) -> None:
    ks = [s["k"] for s in summary]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

    ax1.errorbar(ks, [s["mean_count"] for s in summary],
                 yerr=[s["std_count"] for s in summary], marker="o", capsize=3)
    ax1.set_title("Switches with 2+ failed links (count)")
    ax1.set_ylabel("Number of switches")

    ax2.errorbar(ks, [100 * s["mean_fraction"] for s in summary],
                 yerr=[100 * s["std_fraction"] for s in summary], marker="o", capsize=3)
    ax2.set_title("Switches with 2+ failed links (share)")
    ax2.set_ylabel("Share of all switches (%)")

    for ax in (ax1, ax2):
        ax.set_xlabel("Switch port count k")
        ax.set_xticks(ks)
        ax.grid(alpha=0.3)

    fig.suptitle("Fixed link failure rate, varying switch port count")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Switches with 2+ failed links vs. k.")
    parser.add_argument("--config", required=True, help="JSON config, see configs/switches_1pct.json")
    args = parser.parse_args(argv)

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)

    k_values = cfg["k_values"]
    rate = cfg["failure_rate"]
    seeds = range(cfg.get("num_seeds", 30))
    out_dir = Path(cfg.get("out_dir", "results/switches_1pct"))
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = run(k_values, rate, seeds)
    summary = summarize(rows)

    write_csv(out_dir / "switches_raw.csv", rows)
    write_csv(out_dir / "switches_summary.csv", summary)
    plot_summary(summary, out_dir / "switches_vs_k.png")

    print(f"{'k':>3} {'failed':>7} {'switches':>9} {'mean':>8} {'std':>8} {'share%':>8} {'runs':>5}")
    for s in summary:
        print(f"{s['k']:>3} {s['failed_links']:>7} {s['total_switches']:>9} "
              f"{s['mean_count']:>8.2f} {s['std_count']:>8.2f} "
              f"{100 * s['mean_fraction']:>8.2f} {s['runs']:>5}")
    print(f"\nwrote {out_dir}/switches_summary.csv, switches_raw.csv, switches_vs_k.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
