from failures import inject_failures
from fattree import build_fat_tree
from metrics import reachable_host_pairs


def test_healthy_network_all_pairs_reachable():
    # k=4 has 16 hosts -> 16*15/2 = 120 pairs
    good, total = reachable_host_pairs(build_fat_tree(4))
    assert (good, total) == (120, 120)


def test_all_fabric_links_failed_only_same_edge_pairs_remain():
    # Each edge switch keeps its 2 hosts connected to each other: 8 edges x 1 pair.
    damaged, _ = inject_failures(build_fat_tree(4), 1.0, seed=1)
    good, total = reachable_host_pairs(damaged)
    assert (good, total) == (8, 120)


def test_fraction_never_increases_when_more_links_fail():
    g = build_fat_tree(6)
    fractions = []
    for rate in [0.0, 0.1, 0.3, 0.6]:
        damaged, _ = inject_failures(g, rate, seed=5)
        good, total = reachable_host_pairs(damaged)
        fractions.append(good / total)
    assert fractions == sorted(fractions, reverse=True)
