import pytest

from fattree import build_fat_tree
from failures import fabric_links, inject_failures


@pytest.mark.parametrize("k", [4, 6])
def test_fabric_link_count(k):
    # Switch-to-switch links: k^3/2 in a k-ary fat-tree.
    assert len(fabric_links(build_fat_tree(k))) == k**3 // 2


def test_rate_zero_changes_nothing():
    g = build_fat_tree(4)
    damaged, failed = inject_failures(g, 0.0, seed=1)
    assert failed == []
    assert damaged.number_of_edges() == g.number_of_edges()


def test_failed_count_matches_rate():
    g = build_fat_tree(4)                   # 32 fabric links
    _, failed = inject_failures(g, 0.05, seed=1)
    assert len(failed) == round(0.05 * 32)  # = 2


def test_rate_one_fails_every_fabric_link():
    g = build_fat_tree(4)
    damaged, failed = inject_failures(g, 1.0, seed=1)
    assert len(failed) == len(fabric_links(g))
    assert fabric_links(damaged) == []


def test_host_links_are_never_failed():
    g = build_fat_tree(4)
    damaged, _ = inject_failures(g, 1.0, seed=1)
    hosts = [n for n, d in damaged.nodes(data=True) if d["kind"] == "host"]
    assert all(damaged.degree(h) == 1 for h in hosts)


def test_same_seed_gives_same_failures():
    g = build_fat_tree(6)
    _, a = inject_failures(g, 0.1, seed=7)
    _, b = inject_failures(g, 0.1, seed=7)
    assert a == b


def test_different_seeds_usually_give_different_failures():
    g = build_fat_tree(6)
    _, a = inject_failures(g, 0.1, seed=1)
    _, b = inject_failures(g, 0.1, seed=2)
    assert a != b


def test_original_graph_is_not_modified():
    g = build_fat_tree(4)
    before = g.number_of_edges()
    inject_failures(g, 0.5, seed=3)
    assert g.number_of_edges() == before


@pytest.mark.parametrize("rate", [-0.1, 1.5])
def test_invalid_rate_raises(rate):
    with pytest.raises(ValueError):
        inject_failures(build_fat_tree(4), rate, seed=1)
