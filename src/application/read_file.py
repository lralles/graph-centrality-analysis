import pandas as pd
import networkx as nx

def read_file(edge1_col: str, edge2_col: str, weight_col: str, file_path: str) -> nx.Graph:
    # read file
    df = pd.read_csv(file_path, sep="\t")

    # build graph - assumes not directed
    G = nx.Graph()
    for _, row in df.iterrows():
        # ignore self edges
        if row[edge1_col] == row[edge2_col]:
            continue
        G.add_edge(row[edge1_col], row[edge2_col], weight=row[weight_col])

    return G