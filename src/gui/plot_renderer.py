import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Any
from matplotlib import cm, colors
import networkx as nx


class PlotRenderer:
    def __init__(self, layout_cache):
        self.layout_cache = layout_cache

    def render(self, figure: Figure, result: dict[str, Any]) -> None:
        G = result["graph"]
        impact = result["impact"]
        removed_nodes = result["removed_nodes"]
        size = G.number_of_nodes()

        figure.clf()
        ax = figure.add_subplot(111)

        key = (result["gtype"], size)
        pos = self.layout_cache.get(key)
        if pos is None:
            if size >= 500:
                pos = nx.spring_layout(G, seed=42, k=1 / np.sqrt(size))
            else:
                pos = nx.spring_layout(G, seed=42)
            self.layout_cache.set(key, pos)

        max_abs = max((abs(v) for v in impact.values()), default=0.0)
        if max_abs == 0:
            norm = colors.TwoSlopeNorm(vmin=-1.0, vcenter=0.0, vmax=1.0)
        else:
            norm = colors.TwoSlopeNorm(vmin=-max_abs, vcenter=0.0, vmax=max_abs)

        cmap = plt.get_cmap("bwr")
        node_colors = []
        for n in G.nodes():
            if n in removed_nodes:
                node_colors.append("yellow")
            else:
                node_colors.append(cmap(norm(impact.get(n, 0.0))))

        if size >= 500:
            node_size = 10
            min_thick, max_thick = 0.1, 0.8
        elif size >= 100:
            node_size = 25
            min_thick, max_thick = 0.2, 1.2
        else:
            node_size = 200
            min_thick, max_thick = 0.4, 3.0

        edges_all = list(G.edges())
        weights_all = [G[u][v].get("weight", 1.0) for u, v in edges_all]
        if len(weights_all) > 0:
            w = np.array(weights_all, dtype=float)
            w_min = float(np.min(w))
            w_max = float(np.max(w))
            if w_max == w_min:
                widths_all = [0.5 * (min_thick + max_thick)] * len(weights_all)
            else:
                widths_all = list(min_thick + (w - w_min) / (w_max - w_min) * (max_thick - min_thick))
        else:
            widths_all = []

        removed_set = set(removed_nodes)
        highlight_edges = []
        highlight_widths = []
        base_edges = []
        base_widths = []
        for (e, w) in zip(edges_all, widths_all):
            u, v = e
            if u in removed_set or v in removed_set:
                highlight_edges.append((u, v))
                highlight_widths.append(w)
            else:
                base_edges.append((u, v))
                base_widths.append(w)

        nx.draw_networkx_nodes(
            G,
            pos,
            node_color=node_colors,
            node_size=node_size,
            linewidths=0.8,
            edgecolors="black",
            ax=ax,
        )

        if base_edges:
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=base_edges,
                edge_color="lightgrey",
                width=base_widths,
                ax=ax,
            )

        if highlight_edges:
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=highlight_edges,
                edge_color="orange",
                style="dashed",
                width=highlight_widths,
                ax=ax,
            )

        nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_color="#111")
        ax.set_title(result["label"])
        sm = cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        figure.colorbar(sm, ax=ax, fraction=0.04, pad=0.05).set_label("Δ centrality")


