from failures import fabric_links, sample_failures
from fattree import build_fat_tree
from metrics import switches_with_multiple_failures


def test_no_failures_means_no_bad_switches():
    assert switches_with_multiple_failures([]) == 0


def test_disjoint_failures_do_not_count():
    # Two failed links that share no switch.
    assert switches_with_multiple_failures([("a", "b"), ("c", "d")]) == 0


def test_two_failures_sharing_a_switch_count_once():
    # Switch "a" loses two links; "b" and "c" lose one each.
    assert switches_with_multiple_failures([("a", "b"), ("a", "c")]) == 1


def test_path_of_three_failures_counts_two_switches():
    # "b" and "c" each lose two links; "a" and "d" lose one each.
    assert switches_with_multiple_failures([("a", "b"), ("b", "c"), ("c", "d")]) == 2


def test_star_of_three_failures_counts_center_once():
    assert switches_with_multiple_failures([("x", "a"), ("x", "b"), ("x", "c")]) == 1


def test_sample_failures_count_matches_rate():
    links = fabric_links(build_fat_tree(4))  # 32 fabric links
    assert len(sample_failures(links, 0.05, seed=1)) == 2


def test_sample_failures_same_seed_same_result():
    links = fabric_links(build_fat_tree(6))
    assert sample_failures(links, 0.1, seed=3) == sample_failures(links, 0.1, seed=3)


def test_k4_at_one_percent_fails_nothing():
    # 1% of 32 links is 0.32, which rounds to 0 failed links.
    links = fabric_links(build_fat_tree(4))
    assert sample_failures(links, 0.01, seed=0) == []
