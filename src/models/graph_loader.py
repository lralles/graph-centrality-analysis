import pandas as pd
import networkx as nx

class GraphLoader:
    def load(self, edge1: str, edge2: str, weight: str, path: str) -> nx.Graph:
        df = pd.read_csv(path, sep="\t")
        G = nx.Graph()
        for _, row in df.iterrows():
            if row[edge1] == row[edge2]:
                continue
            G.add_edge(row[edge1], row[edge2], weight=row[weight])
        return G


