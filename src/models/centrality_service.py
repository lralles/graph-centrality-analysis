from typing import Any
import time
import numpy as np
import pandas as pd
import networkx as nx

def get_node_removal_impact(graph, nodes_to_remove, centrality_metric_function):
    start_time = time.time()

    original_centrality = centrality_metric_function(graph)

    temp_graph = graph.copy()
    for node in nodes_to_remove:
        temp_graph.remove_node(node)

    new_centrality = centrality_metric_function(temp_graph)

    impact = {}
    for node in original_centrality:
        if node in nodes_to_remove:
            continue

        old_value = original_centrality[node]
        new_value = new_centrality.get(node, 0)
        delta = new_value - old_value
        impact[node] = delta

    elapsed_time = time.time() - start_time

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


class CentralityAnalysisService:
    def compute(self, G: nx.Graph, removed_nodes, selected_centralities) -> tuple[pd.DataFrame, dict[Any, float]]:
        overall_centrality_delta = {}
        overall_centrality_score = {}

        for centrality in selected_centralities:
            _, node_removal_impact, new_centrality = get_node_removal_impact(
                G, removed_nodes, centrality_functions[centrality]
            )

            for k, v in node_removal_impact.items():
                overall_centrality_delta[k] = overall_centrality_delta.get(k, 0) + v

            for k, v in new_centrality.items():
                overall_centrality_score[k] = overall_centrality_score.get(k, 0) + v

        centrality_table = {}
        for node in overall_centrality_score:
            new_val = overall_centrality_score[node]
            diff = overall_centrality_delta.get(node, np.nan)
            centrality_table[node] = {"new": new_val, "diff": diff}

        df = pd.DataFrame.from_dict(centrality_table, orient="index")
        return df, overall_centrality_delta


