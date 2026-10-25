"""
Link-failure model for the fat-tree.

Only switch-to-switch links ("fabric links") can fail. Host-to-edge links are
left intact, so a failure never disconnects a host from its own edge switch.
"""

import random

import networkx as nx


def fabric_links(g: nx.Graph) -> list:
    """Return all switch-to-switch links as (u, v) tuples."""
    return [
        (u, v)
        for u, v in g.edges()
        if g.nodes[u]["kind"] != "host" and g.nodes[v]["kind"] != "host"
    ]


def sample_failures(links: list, rate: float, seed: int) -> list:
    """
    Choose a random subset of links to fail.

    Args:
        links: the candidate links (for example from fabric_links).
        rate:  fraction of links to fail, in [0, 1].
        seed:  random seed, so the same inputs always fail the same links.

    Returns:
        A list of round(rate * len(links)) distinct links.
    """
    if not 0.0 <= rate <= 1.0:
        raise ValueError(f"failure rate must be in [0, 1], got {rate}")

    # Sort first so the sample depends only on the seed, not on the input order.
    ordered = sorted(links, key=repr)
    n_fail = round(rate * len(ordered))
    return random.Random(seed).sample(ordered, n_fail)


def inject_failures(g: nx.Graph, rate: float, seed: int):
    """
    Remove a random fraction of fabric links.

    Args:
        g:    the healthy topology (not modified).
        rate: fraction of fabric links to fail, in [0, 1].
        seed: random seed, so the same inputs always fail the same links.

    Returns:
        (damaged_graph, failed_links) where damaged_graph is a copy of g
        with the failed links removed.
    """
    failed = sample_failures(fabric_links(g), rate, seed)

    damaged = g.copy()
    damaged.remove_edges_from(failed)
    return damaged, failed
