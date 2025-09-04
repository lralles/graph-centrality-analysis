import networkx as nx
import random

# returns a graph
def make_graph(
    graph_type: str,
    size: int,
    directed: bool = False,
    weighted: bool = False,
    weight_range: tuple = (1.0, 10.0),
    seed: int = 42,
) -> nx.Graph:
    if graph_type == "erdos_renyi":
        c = 5
        p = c / size
        # directions are decided by the p parameter (randomized)
        G = nx.erdos_renyi_graph(size, p, seed=seed, directed=directed)
    
    elif graph_type == "barabasi_albert":
        m = max(2, size // 50)

        G = nx.barabasi_albert_graph(size, m, seed=seed)

        if directed:
            # simetric directed
            G = G.to_directed()
    
    elif graph_type == "watts_strogatz":
        k = max(2, size // 50)
        G = nx.watts_strogatz_graph(size, k, 0.3, seed=seed)
        if directed:
            # simetric directed
            G = G.to_directed()
    else:
        # satisfy compiler
        raise ValueError(f"Unsupported graph_type: {graph_type}")

    if weighted:
        # adds random weights to the edges with uniform distribution
        rng = random.Random(seed)
        low, high = weight_range

        # go through all edges and add random weights
        for u, v in G.edges():
            w = rng.uniform(float(low), float(high))
            G[u][v]['weight'] = w

    return G

# returns the highest degree node for targeted removal
def highest_degree_node(G: nx.Graph):
    return max(G.degree, key=lambda x: x[1])[0]

# debug method for results
def debug(results):
    for r in results:
        print(f"graph={r['graph_type']}, size={r['size']}, metric={r['metric']}")

        items = list(r["impact"].items())
        items_to_show = items
        
        print({n: round(v, 6) for n, v in items_to_show})
