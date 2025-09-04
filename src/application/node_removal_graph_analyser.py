import time
import networkx as nx

plot = True

def get_node_removal_impact(graph, nodes_to_remove, centrality_metric_function):
    start_time = time.time()

    # compute old
    original_centrality = centrality_metric_function(graph)
    #print(original_betweeness)

    # compute new
    temp_graph = graph.copy()
    for node in nodes_to_remove:
        temp_graph.remove_node(node)

    new_centrality = centrality_metric_function(temp_graph)
    #print(new_betweeness)
    # compare
    impact = {}

    for node in original_centrality:
        if node in nodes_to_remove:
            continue

        old_value = original_centrality[node]
        new_value = new_centrality.get(node, 0)
        delta = new_value - old_value

        impact[node] = delta

    elapsed_time = time.time() - start_time

    # report
    impact_sorted = dict(sorted(impact.items(), key=lambda x: x[1], reverse=True))

    return elapsed_time, impact_sorted, new_centrality

def print_impact(impact):
    for node, delta in impact.items():
        print(f"Node {node}: Δ centrality = {delta:.4f}")

    print('\n')

centrality_functions = {
    "degree": nx.degree_centrality,
    "betweenness": nx.betweenness_centrality,
    "closeness": nx.closeness_centrality,
    "eigenvector": lambda G: nx.eigenvector_centrality(G, max_iter=5000),
    "katz": lambda G: nx.katz_centrality_numpy(G, alpha=0.01, beta=1.0),
}
