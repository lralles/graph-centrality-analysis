from itertools import product
from tkinter import NONE
import networkx as nx

# graph types being tested - additions here must be reflected in the get_graph_and_node_to_remove method (bellow)
GRAPH_TYPES = [
    "erdos_renyi", 
    "watts_strogatz", 
    "barabasi_albert"
]

# graph sizes being tested
SIZES = [10, 100]

# centrality metrics being tested (each method takes a graph G as input)
CENTRALITY_METRICS = {
    "degree": nx.degree_centrality,
    "betweenness": nx.betweenness_centrality,
    "closeness": nx.closeness_centrality,
    "eigenvector": lambda G: nx.eigenvector_centrality(G, max_iter=1000),
    "pagerank": nx.pagerank,
    "harmonic": nx.harmonic_centrality,
}

# creates a config object for each combinaltion of the configurations above
analysis_config = [
    {
        "graph_type": gtype,
        "size": size,
        "metric_name": mname,
        "metric_func": mfunc
    }
    for gtype, size, (mname, mfunc) in product(GRAPH_TYPES, SIZES, CENTRALITY_METRICS.items())
]


def get_graph_and_node_to_remove(graph_type, size, seed=None):
    match graph_type:
        case "path":
            G = nx.path_graph(size)
            # remove middle node
            node = size // 2
        case "cycle":
            G = nx.cycle_graph(size)
            # remove middle node
            node = size // 2
        case "star":
            G = nx.star_graph(size - 1)
            # remove center node
            node = 0
        case "complete":
            G = nx.complete_graph(size)
            # any node
            node = 0
        case "wheel":
            G = nx.wheel_graph(size)
            # any node
            node = 0
        case "grid":
            # this graph is a grid (2d square), so the size is the sqrt of the graph intended size
            grid_size = int(size**0.5)
            G = nx.grid_2d_graph(grid_size, grid_size)
            # in this graph, the nodes are indexed as tuples, so this is the middle node
            node = (grid_size // 2, grid_size // 2)
        case "erdos_renyi":
            c = 5
            p = c / size
            G = nx.erdos_renyi_graph(size, p, seed=seed, directed=False)
        case "barabasi_albert":
            m = max(2, size // 50)
            G = nx.barabasi_albert_graph(size, m, seed=seed)        
        case "watts_strogatz":
            k = max(2, size // 50)
            G = nx.watts_strogatz_graph(size, k, 0.3, seed=seed)

    return G, node
