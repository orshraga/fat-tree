import pytest

from fattree import build_fat_tree, describe


@pytest.mark.parametrize("k", [2, 4, 6, 8])
def test_counts_match_formulas(k):
    g = build_fat_tree(k)
    counts = describe(g)

    assert counts["host"] == k**3 // 4
    assert counts["edge"] == k * k // 2
    assert counts["agg"] == k * k // 2
    assert counts["core"] == (k // 2) ** 2
    assert counts["links"] == 3 * k**3 // 4


@pytest.mark.parametrize("k", [2, 4, 6])
def test_every_host_has_one_link(k):
    g = build_fat_tree(k)
    hosts = [n for n, d in g.nodes(data=True) if d["kind"] == "host"]
    assert all(g.degree(h) == 1 for h in hosts)


@pytest.mark.parametrize("k", [4, 6])
def test_switch_degrees_are_k(k):
    # In a k-ary fat-tree every switch uses exactly k ports.
    g = build_fat_tree(k)
    for n, d in g.nodes(data=True):
        if d["kind"] != "host":
            assert g.degree(n) == k, f"{n} has degree {g.degree(n)}"


@pytest.mark.parametrize("k", [0, 1, 3, -4])
def test_invalid_k_raises(k):
    with pytest.raises(ValueError):
        build_fat_tree(k)
