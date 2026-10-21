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

    The number of failed links is round(rate * number_of_fabric_links).
    Python's round() rounds halves to the nearest even integer.
    """
    if not 0.0 <= rate <= 1.0:
        raise ValueError(f"failure rate must be in [0, 1], got {rate}")

    # Sort first so the sample depends only on the seed, not on dict/edge order.
    links = sorted(fabric_links(g), key=repr)
    n_fail = round(rate * len(links))
    failed = random.Random(seed).sample(links, n_fail)

    damaged = g.copy()
    damaged.remove_edges_from(failed)
    return damaged, failed
