"""
Fat-tree topology generator (Al-Fares et al., SIGCOMM 2008).

A k-ary fat-tree is built from identical k-port switches and has:
  - k pods
  - each pod: k/2 edge switches and k/2 aggregation switches
  - each edge switch: k/2 hosts
  - (k/2)^2 core switches

Node naming (tuples, so they are easy to read and to test):
  ("host", pod, edge, idx)   host number idx under edge switch (pod, edge)
  ("edge", pod, e)           edge switch e in pod
  ("agg",  pod, a)           aggregation switch a in pod
  ("core", j, i)             core switch in group j, position i
"""

import argparse

import networkx as nx


def build_fat_tree(k: int) -> nx.Graph:
    """Return the k-ary fat-tree as an undirected networkx graph."""
    if k < 2 or k % 2 != 0:
        raise ValueError(f"k must be an even integer >= 2, got {k}")

    half = k // 2
    g = nx.Graph()

    for pod in range(k):
        for e in range(half):
            edge = ("edge", pod, e)
            g.add_node(edge, kind="edge", pod=pod)

            # Hosts under this edge switch
            for idx in range(half):
                host = ("host", pod, e, idx)
                g.add_node(host, kind="host", pod=pod)
                g.add_edge(host, edge)

            # Every edge switch connects to every aggregation switch in its pod
            for a in range(half):
                g.add_edge(edge, ("agg", pod, a))

        for a in range(half):
            agg = ("agg", pod, a)
            g.add_node(agg, kind="agg", pod=pod)

            # Aggregation switch a connects to core group a
            for i in range(half):
                core = ("core", a, i)
                g.add_node(core, kind="core")
                g.add_edge(agg, core)

    return g


def describe(g: nx.Graph) -> dict:
    """Count nodes and links by type."""
    counts = {"host": 0, "edge": 0, "agg": 0, "core": 0}
    for _, data in g.nodes(data=True):
        counts[data["kind"]] += 1
    counts["links"] = g.number_of_edges()
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a k-ary fat-tree topology.")
    parser.add_argument("--k", type=int, required=True, help="ports per switch (even, >= 2)")
    args = parser.parse_args()

    g = build_fat_tree(args.k)
    counts = describe(g)

    print(f"k = {args.k}")
    for name, value in counts.items():
        print(f"  {name:<6} {value}")


if __name__ == "__main__":
    main()
