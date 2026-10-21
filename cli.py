"""
Command-line interface: build a fat-tree, inject link failures, report connectivity.

Settings come from three places, in increasing priority:
  1. built-in defaults
  2. a JSON config file (--config)
  3. command-line flags

Example:
  python cli.py --k 4 --failure-rate 0.05 --seed 1
  python cli.py --config configs/example.json
  python cli.py --config configs/example.json --seed 7
"""

import argparse
import json

from fattree import build_fat_tree, describe
from failures import fabric_links, inject_failures
from metrics import reachable_host_pairs

DEFAULTS = {"k": None, "failure_rate": 0.0, "seed": 42}


def load_config(path: str) -> dict:
    """Load a JSON config file. Only the keys in DEFAULTS are allowed."""
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    unknown = set(cfg) - set(DEFAULTS)
    if unknown:
        raise ValueError(f"unknown keys in config {path}: {sorted(unknown)}")
    return cfg


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Build a k-ary fat-tree, fail a fraction of its fabric links, "
                    "and report how many host pairs stay connected."
    )
    p.add_argument("--k", type=int, help="ports per switch (even, >= 2)")
    p.add_argument("--failure-rate", type=float,
                   help="fraction of switch-to-switch links to fail, in [0, 1] (default 0.0)")
    p.add_argument("--seed", type=int, help="random seed for failures (default 42)")
    p.add_argument("--config", help="JSON file with keys k, failure_rate, seed; "
                                    "command-line flags override it")
    return p


def resolve_settings(args: argparse.Namespace) -> dict:
    settings = dict(DEFAULTS)
    if args.config:
        settings.update(load_config(args.config))
    for key in DEFAULTS:
        value = getattr(args, key)
        if value is not None:
            settings[key] = value
    if settings["k"] is None:
        raise ValueError("k is required (use --k or set it in the config file)")
    return settings


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        s = resolve_settings(args)
        healthy = build_fat_tree(s["k"])
        damaged, failed = inject_failures(healthy, s["failure_rate"], s["seed"])
    except ValueError as e:
        parser.error(str(e))  # prints the message and exits with code 2

    counts = describe(healthy)
    good, total = reachable_host_pairs(damaged)

    print(f"k = {s['k']}")
    print(f"hosts: {counts['host']}, switches: {counts['edge'] + counts['agg'] + counts['core']}, "
          f"links: {counts['links']} (fabric: {len(fabric_links(healthy))})")
    print(f"failure rate: {s['failure_rate']} (seed {s['seed']})")
    print(f"failed fabric links: {len(failed)} of {len(fabric_links(healthy))}")
    print(f"reachable host pairs: {good} of {total} ({good / total:.1%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
