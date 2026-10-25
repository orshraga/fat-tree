"""
Metrics for a (possibly damaged) fat-tree.
"""

from collections import Counter

import networkx as nx


def host_nodes(g: nx.Graph) -> list:
    """Return all host nodes."""
    return [n for n, d in g.nodes(data=True) if d["kind"] == "host"]


def reachable_host_pairs(g: nx.Graph):
    """
    Count unordered host pairs that can still reach each other.

    Returns:
        (connected_pairs, total_pairs)

    Two hosts are connected if they lie in the same connected component.
    A component with c hosts contributes c*(c-1)/2 connected pairs.
    total_pairs is H*(H-1)/2 for H hosts.
    """
    hosts = set(host_nodes(g))
    total = len(hosts) * (len(hosts) - 1) // 2

    connected = 0
    for component in nx.connected_components(g):
        c = len(component & hosts)
        connected += c * (c - 1) // 2

    return connected, total


def switches_with_multiple_failures(failed_links) -> int:
    """
    Count switches that lose two or more of their links.

    failed_links: iterable of (u, v) pairs, as returned by sample_failures.
    Only fabric links can fail, so every node in these pairs is a switch.
    """
    touches = Counter()
    for u, v in failed_links:
        touches[u] += 1
        touches[v] += 1
    return sum(1 for n in touches.values() if n >= 2)
