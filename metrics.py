"""
Metrics for a (possibly damaged) fat-tree.
"""

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
