import networkx as nx

# returns a graph
def make_graph(graph_type: str, size: int) -> nx.Graph:
    if graph_type == "erdos_renyi":
        c = 5
        p = c / size
        return nx.erdos_renyi_graph(size, p, seed=42)
    
    if graph_type == "barabasi_albert":
        m = max(2, size // 50)
        return nx.barabasi_albert_graph(size, m, seed=42)
    
    if graph_type == "watts_strogatz":
        k = max(2, size // 50)
        return nx.watts_strogatz_graph(size, k, 0.3, seed=42)

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
