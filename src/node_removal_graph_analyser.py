import time

plot = True

def get_node_removal_impact(graph, node_to_remove, centrality_metric_function):
    start_time = time.time()

    # compute old
    original_betweeness = centrality_metric_function(graph)
    #print(original_betweeness)

    # compute new
    temp_graph = graph.copy()
    temp_graph.remove_node(node_to_remove)

    new_betweeness = centrality_metric_function(temp_graph)
    #print(new_betweeness)
    # compare
    impact = {}

    for node in original_betweeness:
        if node == node_to_remove:
            continue

        old_value = original_betweeness[node]
        new_value = new_betweeness.get(node, 0)
        delta = new_value - old_value

        impact[node] = delta

    elapsed_time = time.time() - start_time

    # report
    impact_sorted = dict(sorted(impact.items(), key=lambda x: x[1], reverse=True))

    return elapsed_time, impact_sorted

def print_impact(impact):
    for node, delta in impact.items():
        print(f"Node {node}: Δ centrality = {delta:.4f}")

    print('\n')

