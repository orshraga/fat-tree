# Fat-Tree Topology: Generation and Link-Failure Analysis

Homework 1. Builds a k-ary fat-tree (Al-Fares, Loukissas, Vahdat, SIGCOMM 2008),
fails a random fraction of its switch-to-switch links, and measures how many host
pairs remain connected.

## Status

- [x] Topology generator for any even k ≥ 2 (`fattree.py`)
- [x] Link-failure model, switch-to-switch links only, seeded (`failures.py`)
- [x] Basic metric: fraction of reachable host pairs (`metrics.py`)
- [x] Command-line interface with JSON config support (`cli.py`)
- [x] Failure-rate sweep with CSV output and matplotlib plot (`experiment.py`)
- [ ] Results and discussion (after running the sweep)

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Running a single scenario

```powershell
python cli.py --k 4 --failure-rate 0.05 --seed 1
```

Output:

```
k = 4
hosts: 16, switches: 20, links: 48 (fabric: 32)
failure rate: 0.05 (seed 1)
failed fabric links: 2 of 32
reachable host pairs: 118 of 120 (98.3%)
```

Or from a config file:

```powershell
python cli.py --config configs/example.json
python cli.py --config configs/example.json --seed 7
```

### Input parameters

| Parameter | CLI flag | Config key | Type | Default | Meaning |
|---|---|---|---|---|---|
| Switch port count | `--k` | `k` | int | required | Ports per switch. Must be even and ≥ 2. Gives k³/4 hosts. |
| Failure rate | `--failure-rate` | `failure_rate` | float | 0.0 | Fraction of **switch-to-switch** links that fail, in [0, 1]. |
| Random seed | `--seed` | `seed` | int | 42 | Seed for choosing failed links. Same seed, same failures. |
| Config file | `--config` | — | path | — | JSON file with the keys above. CLI flags override it. |

Precedence: built-in defaults < config file < command-line flags.
Unknown keys in a config file are rejected.

### Sweep experiment

```powershell
python experiment.py --config configs/sweep.json
```

`configs/sweep.json` keys:

| Key | Meaning |
|---|---|
| `k_values` | list of port counts to test |
| `failure_rates` | list of failure rates to test |
| `num_seeds` | number of random seeds per (k, rate) pair; runs use seeds 0 … num_seeds−1 |
| `out_dir` | output folder (created if missing) |

Outputs in `out_dir`:
- `reachability_raw.csv`: one row per (k, rate, seed)
- `reachability_summary.csv`: mean and standard deviation per (k, rate)
- `reachability_vs_failure.png`: plot of the mean with standard-deviation error bars

## Failure model

- **Scope:** only switch-to-switch links (edge↔aggregation and aggregation↔core) can fail.
  Host↔edge links never fail, so a host is never disconnected from its own edge switch by a failure.
  Failing host links as well is left for future work.
- **Count:** the number of failed links is `round(rate × number_of_fabric_links)`.
  For k=4 there are 32 fabric links, so rate 0.05 fails round(1.6) = 2 links.
  Python's `round` sends halves to the nearest even number.
- **Selection:** links are sorted into a fixed order, then a uniform random sample is drawn with `random.Random(seed)`.
  The result depends only on (k, rate, seed).
- **Independence:** failures are independent and uniform. No correlation between links, and no switch-level failures.

## Metric: reachable host pairs

For a damaged graph with H hosts:

```
reachable fraction = (Σ over components c of  h_c·(h_c − 1)/2) / (H·(H − 1)/2)
```

where h_c is the number of hosts in connected component c. This is the fraction of
unordered host pairs that still have at least one path between them.

Sanity values for k=4 (16 hosts, 120 pairs):
- no failures: 120 / 120 = 100%
- all fabric links failed: only the pairs under the same edge switch remain, 8 / 120 ≈ 6.7%

## Tests

```powershell
python -m pytest
```

Run with `python -m pytest`, not plain `pytest`, so the project folder is on the import path.

| File | What it checks |
|---|---|
| `tests/test_fattree.py` | Node and link counts match the formulas for k = 2, 4, 6, 8; switch degrees equal k; invalid k is rejected |
| `tests/test_failures.py` | Fabric-link count; rate 0 changes nothing; failed count = round(rate·E); rate 1 removes all fabric links; host links survive; same seed → same failures; original graph is not modified; invalid rate is rejected |
| `tests/test_metrics.py` | Healthy network gives 120/120; all fabric links failed gives 8/120; the fraction never rises as the failure rate rises |
| `tests/test_cli.py` | Output format; config file is read; CLI overrides config; missing k and unknown config keys are errors |

## Topology reference

| Element | Count (k-ary fat-tree) |
|---|---|
| Pods | k |
| Edge switches | k²/2 |
| Aggregation switches | k²/2 |
| Core switches | (k/2)² |
| Hosts | k³/4 |
| Fabric links (switch-to-switch) | k³/2 |
| Total links | 3k³/4 |

Each pod has k/2 edge and k/2 aggregation switches. Every edge switch connects to every
aggregation switch in its pod. Aggregation switch `a` in each pod connects to core group `a`
(k/2 core switches).

## Results

*To be filled in after running `experiment.py`. Each plot needs: the setup and parameters,
the observed result, and an explanation of why it matters.*

### Example 1: Reachable host pairs vs. failure rate, for k = 4, 6, 8

- **Setup:** `configs/sweep.json`, 30 seeds per point, failure rates 0 to 20%, switch-to-switch links only.
- **Observed:** *(to write)*
- **Interpretation:** *(to write)*

## Files

| File | Purpose |
|---|---|
| `fattree.py` | Builds the topology (`build_fat_tree`) and counts its parts (`describe`) |
| `failures.py` | Chooses and removes failed links (`fabric_links`, `inject_failures`) |
| `metrics.py` | Reachable host pairs (`reachable_host_pairs`) |
| `cli.py` | Command-line entry point for a single scenario |
| `experiment.py` | Seed sweep, CSV output, plot |
| `configs/example.json` | Example single-run config |
| `configs/sweep.json` | Sweep config |
| `tests/` | pytest suite |
