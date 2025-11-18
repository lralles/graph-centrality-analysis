from typing import Any
import time
import numpy as np
import pandas as pd
import networkx as nx

def get_node_removal_impact(graph, nodes_to_remove, centrality_metric_function):
    """
     Calculate the impact of removing specific nodes on the centrality of remaining nodes.
    
    This function computes how the centrality values of nodes in a graph change when
    a specified set of nodes is removed. It measures the difference between the original
    centrality and the new centrality after node removal.
    
    Parameters
    ----------
    graph : networkx.Graph
    nodes_to_remove : list or set
    centrality_metric_function : callable
    Returns
    -------
    tuple[float, dict, dict]
        A tuple containing:
        - elapsed_time (float)
        - impact_sorted (dict)
        - new_centrality (dict)
    """
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

def unnormalized_degree_centrality(G):
    """
    Compute the unnormalized degree centrality for nodes.
    Parameters
    ----------
    G : NetworkX graph
        A NetworkX graph

    Returns
    -------
    dict
        Dictionary of nodes with unnormalized degree centrality as values.
    """
    return dict(G.degree())



def calculate_diameter(G):
    """
    Calculate the diameter of a graph (longest shortest path between any two nodes).
    Returns infinity if the graph is disconnected.

    Parameters
    ----------
    G : NetworkX graph
        A NetworkX graph

    Returns
    -------
    float
        The diameter of the graph, or float('inf') if disconnected
    """
    if G.number_of_nodes() == 0:
        return 0

    if G.number_of_nodes() == 1:
        return 0
    
    try:
        return nx.diameter(G)
    except nx.NetworkXError:
        return float('inf')



centrality_functions = {
    "degree": nx.degree_centrality,
    "unnormalized_degree": unnormalized_degree_centrality,
    "betweenness": nx.betweenness_centrality,
    "closeness": nx.closeness_centrality,
    "eigenvector": lambda G: nx.eigenvector_centrality(G, max_iter=5000),
    "katz": lambda G: nx.katz_centrality_numpy(G, alpha=0.01, beta=1.0),
}


class CentralityAnalysisService:
    def compute(self, G: nx.Graph, removed_nodes, selected_centralities) -> tuple[pd.DataFrame, dict[Any, float], dict[str, float]]:
        start_time = time.time()
        # Calculate diameter before node removal
        diameter_before = calculate_diameter(G)

        # Create a copy of the graph for diameter calculation after removal
        temp_graph = G.copy()
        for node in removed_nodes:
            temp_graph.remove_node(node)

        # Calculate diameter after node removal
        diameter_after = calculate_diameter(temp_graph)

        diameter_info = {
            'before': diameter_before,
            'after': diameter_after
        }

        overall_centrality_delta = {}
        centrality_results = {}  # Store individual centrality results

        for centrality in selected_centralities:
            _, node_removal_impact, new_centrality = get_node_removal_impact(
                G, removed_nodes, centrality_functions[centrality]
            )

            # Store individual centrality results
            centrality_results[centrality] = {
                'new': new_centrality,
                'diff': node_removal_impact
            }

            for k, v in node_removal_impact.items():
                overall_centrality_delta[k] = overall_centrality_delta.get(k, 0) + v

        # Build the table with individual centrality columns
        centrality_table = {}
        all_nodes = set()

        # Collect all nodes from all centrality measures
        for centrality_data in centrality_results.values():
            all_nodes.update(centrality_data['new'].keys())

        for node in all_nodes:
            row_data = {}

            # Add individual centrality columns
            for centrality in selected_centralities:
                new_val = centrality_results[centrality]['new'].get(node, np.nan)
                diff_val = centrality_results[centrality]['diff'].get(node, np.nan)
                row_data[f"{centrality.title()}"] = new_val
                row_data[f"Δ {centrality.title()}"] = diff_val

            # Add combined columns
            combined_new = sum(centrality_results[cent]['new'].get(node, 0) for cent in selected_centralities)
            combined_diff = sum(centrality_results[cent]['diff'].get(node, 0) for cent in selected_centralities)
            row_data["Combined"] = combined_new
            row_data["Δ Combined"] = combined_diff

            centrality_table[node] = row_data

        df = pd.DataFrame.from_dict(centrality_table, orient="index")

        elapsed_time = time.time() - start_time
        return elapsed_time, df, overall_centrality_delta, diameter_info


