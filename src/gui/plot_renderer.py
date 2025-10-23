import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Any
from matplotlib import cm, colors
import networkx as nx

class PlotRenderer:
    def __init__(self, layout_cache):
        self.layout_cache = layout_cache

    def _calculate_layout(self, G, layout_type: str, size: int):
        if layout_type == "Circular":
            # Use circular layout with better node positioning
            pos = nx.circular_layout(G, scale=1.2)

        else:  # Default to Spring layout
            if size >= 500:
                pos = nx.spring_layout(G, seed=42, k=1 / np.sqrt(size))
            else:
                pos = nx.spring_layout(G, seed=42)

        return pos

    def render(self, figure: Figure, result: dict[str, Any], plot_options: dict[str, bool] = None) -> None:
        """
        Render the graph plot with configurable options.

        Args:
            figure: The matplotlib figure to render on
            result: Dictionary containing graph, impact, removed_nodes, etc.
            plot_options: Dictionary with keys:
                - show_node_names: Whether to display node labels
                - edge_thickness_by_weight: Whether edge thickness reflects weight
                - mark_removed_edges: Whether to highlight edges connected to removed nodes
                - layout_type: Layout algorithm to use ("Spring", "Circular")
        """
        # Default plot options
        if plot_options is None:
            plot_options = {
                "show_node_names": True,
                "edge_thickness_by_weight": True,
                "mark_removed_edges": True,
                "layout_type": "Spring",
            }

        G = result["graph"]
        impact = result["impact"]
        removed_nodes = result["removed_nodes"]
        size = G.number_of_nodes()

        figure.clf()
        # Create subplot that fills the entire figure area
        ax = figure.add_subplot(111)

        # Remove axis borders and ticks to maximize graph area
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)  # Also hide the left spine

        # Get layout type from plot options
        layout_type = plot_options.get("layout_type", "Spring")

        # Create cache key that includes layout type and graph structure
        # Use a hash of the graph structure to ensure different graphs get different layouts
        graph_hash = hash(tuple(sorted(G.edges())))
        key = (result["gtype"], size, layout_type, graph_hash)

        pos = self.layout_cache.get(key)
        if pos is None:
            pos = self._calculate_layout(G, layout_type, size)
            self.layout_cache.set(key, pos)

        max_abs = max((abs(v) for v in impact.values()), default=0.0)
        if max_abs == 0:
            norm = colors.TwoSlopeNorm(vmin=-1.0, vcenter=0.0, vmax=1.0)
        else:
            norm = colors.TwoSlopeNorm(vmin=-max_abs, vcenter=0.0, vmax=max_abs)

        cmap = plt.get_cmap("bwr")
        node_colors = []

        # Check if this is a preview (no impact data)
        has_impact_data = impact and any(impact.values())

        for n in G.nodes():
            if n in removed_nodes:
                node_colors.append("yellow")
            elif has_impact_data:
                # Use impact-based coloring for analysis
                node_colors.append(cmap(norm(impact.get(n, 0.0))))
            else:
                # Use neutral color for preview
                node_colors.append("lightblue")

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

        # Calculate edge widths based on plot options
        if plot_options.get("edge_thickness_by_weight", True):
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
        else:
            # Use uniform edge width
            uniform_width = 0.5 * (min_thick + max_thick)
            widths_all = [uniform_width] * len(edges_all)

        # Separate edges based on whether they connect to removed nodes
        removed_set = set(removed_nodes)
        highlight_edges = []
        highlight_widths = []
        base_edges = []
        base_widths = []

        if plot_options.get("mark_removed_edges", True):
            # Separate edges connected to removed nodes
            for (e, w) in zip(edges_all, widths_all):
                u, v = e
                if u in removed_set or v in removed_set:
                    highlight_edges.append((u, v))
                    highlight_widths.append(w)
                else:
                    base_edges.append((u, v))
                    base_widths.append(w)
        else:
            # Treat all edges the same
            base_edges = edges_all
            base_widths = widths_all

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

        # Draw node labels based on plot options
        if plot_options.get("show_node_names", True):
            nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_color="#111")

        # Set a smaller title
        ax.set_title(result["label"], fontsize=10)

        # Remove margins and make the graph fill the whole area
        ax.set_aspect('equal')
        ax.margins(0)

        # Use figure.tight_layout instead of plt.tight_layout for better control
        figure.tight_layout(pad=0.05)

        # Adjust subplot parameters to minimize whitespace with a bit more top margin for title
        figure.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.02)

        # Only show colorbar if there's impact data (not for preview)
        if impact and any(impact.values()):
            sm = cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            # Adjust colorbar positioning when present
            figure.subplots_adjust(left=0.02, right=0.85, top=0.90, bottom=0.02)
            figure.colorbar(sm, ax=ax, fraction=0.04, pad=0.05).set_label("Δ centrality")


