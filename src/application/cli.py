import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless backend


from read_file import read_file
from node_removal_graph_analyser import get_node_removal_impact, centrality_functions
from graph_plot import plot_result


def main():
    parser = argparse.ArgumentParser(description="Graph node removal analysis CLI")
    parser.add_argument("--graph", required=True, help="Path to graph TSV file")
    parser.add_argument("--col-edge1", default="edge1", help="Name of first edge column")
    parser.add_argument("--col-edge2", default="edge2", help="Name of second edge column")
    parser.add_argument("--col-weight", default="weight", help="Name of weight column")
    parser.add_argument("--removed-nodes", nargs="+", required=True, help="Nodes to remove")
    parser.add_argument("--centralities", nargs="+", choices=centrality_functions.keys(),
                        required=True, help="Centrality measures to analyse")
    args = parser.parse_args()

    # step 1 - read file
    G = read_file(args.col_edge1, args.col_edge2, args.col_weight, args.graph)

    # step 2 - analyse and accumulate centrality score and centrality delta
    overall_centrality_delta = {}
    overall_centrality_score = {}

    for centrality in args.centralities:
        _, node_removal_impact, new_centrality = get_node_removal_impact(
            G, args.removed_nodes, centrality_functions[centrality]
        )

        for k, v in node_removal_impact.items():
            overall_centrality_delta[k] = overall_centrality_delta.get(k, 0) + v

        for k, v in new_centrality.items():
            overall_centrality_score[k] = overall_centrality_score.get(k, 0) + v

    # step 3 - build final table using the accumulated results
    centrality_table = {}
    for node in overall_centrality_score:
        new_val = overall_centrality_score[node]
        diff = overall_centrality_delta.get(node, np.nan)

        centrality_table[node] = {"new": new_val, "diff": diff}

    df = pd.DataFrame.from_dict(centrality_table, orient="index")
    print(df)

    # step 4 - plot the result
    result = {
        "label": "Read from TSV",
        "gtype": "Read from TSV",
        "impact": overall_centrality_delta,
        "graph": G,
        "removed_nodes": args.removed_nodes,
    }
    plot_result(result, {}, save_plots=True, showLabels=True, save_path=".")



if __name__ == "__main__":
    main()
