import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm, colors
import networkx as nx

# plot the resulting graphs
def plot_result(result, pos_cache,save_plots = False, showLabels = False, save_path = None):
    label = result["label"]
    impact = result["impact"]
    G = result["graph"]
    gtype = result["gtype"]
    removed_nodes = result["removed_nodes"]
    size = G.number_of_nodes()

    # layout cache per (graph_type, size)
    # This ensures graphs of same size and type are shown with nodes in the same positions
    # The seed is just a random number, 42 is used a pop-culture reference
    # The K parameter here is used to optimize node distances, for larger graphs, it should be smaller
    # the pos value will be used in the plot
    key = (gtype, size)
    if key not in pos_cache:
        if size >= 500:
            pos_cache[key] = nx.spring_layout(G, seed=42, k=1 / np.sqrt(size))
        else:
            pos_cache[key] = nx.spring_layout(G, seed=42)
    pos = pos_cache[key]

    # normalize impacts for color mapping
    # outputs norm, norm is a normalization function created based on the max absolute value
    max_abs = max((abs(v) for v in impact.values()), default=0.0)
    if max_abs == 0:
        norm = colors.TwoSlopeNorm(vmin=-1.0, vcenter=0.0, vmax=1.0)
    else:
        norm = colors.TwoSlopeNorm(vmin=-max_abs, vcenter=0.0, vmax=max_abs)

    # build node colors
    # node_colors stores the colors of each nodes, based on the index
    # cmap creates the blue white red color scheme
    # the removed node gets the yellow color
    # the normalized value by norm is passed to the cmap(bwr) that than returns the color
    cmap = plt.get_cmap("bwr")
    node_colors = []
    for n in G.nodes():
        if n in removed_nodes:
            node_colors.append("yellow")
        else:
            node_colors.append(cmap(norm(impact.get(n, 0.0))))

    # visual parameters by size
    # defined experimentally, based on the used graphs sizes
    if size >= 500:
        node_size = 10
        min_thick, max_thick = 0.1, 0.8
    elif size >= 100:
        node_size = 25
        min_thick, max_thick = 0.2, 1.2
    else:
        node_size = 200
        min_thick, max_thick = 0.4, 3.0

    # compute edge widths from weights
    if G.number_of_edges() > 0:
        weights = [d.get("weight", 1.0) for _, _, d in G.edges(data=True)]
        w = np.array(weights, dtype=float)
        w_min = float(np.min(w))
        w_max = float(np.max(w))
        if w_max == w_min:
            edge_widths = [0.5 * (min_thick + max_thick)] * len(weights)
        else:
            edge_widths = list(min_thick + (w - w_min) / (w_max - w_min) * (max_thick - min_thick))
    else:
        edge_widths = 0.6

    # create figure
    # ax will be used for the colorbar scale
    # 0.8 is the border thickness, used to diffrrentiate from the white background
    fig, ax = plt.subplots(figsize=(6, 5))
    nx.draw(
        G,
        pos,
        node_color=node_colors,
        node_size=node_size,
        edge_color="lightgrey",
        width=edge_widths,
        ax=ax,
        with_labels=showLabels,
        linewidths=0.8,
        edgecolors="black"
    )
    # set label
    ax.set_title(label)

    # colorbar for impact scale
    # creates the color scale on the side of the images, based on the color map and normalized values
    # 0.046 defines the widht of the scale bar in 0,04 the padding to the rest of the plot
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, fraction=0.04, pad=0.05)
    cbar.set_label("Δ centrality")

    if save_plots:
        # save image to results
        safe_filename = label
        if(save_path is None):
            filepath = f"../../results/random-graphs-impact/images/{safe_filename}.svg"
        else: 
            filepath = f"{save_path}/{safe_filename}.svg"
        # Save the plot instead of showing it
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', format='svg')
        plt.close()  # Close the figure to free memory
    else:
        plt.show()

# returns the highest degree node for targeted removal
def highest_degree_node(G: nx.Graph):
    return max(G.degree, key=lambda x: x[1])[0]
