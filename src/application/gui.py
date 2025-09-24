import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from typing import Any, Optional

from node_removal_graph_analyser import get_node_removal_impact, centrality_functions


class ToolbarView(ttk.Frame):
    def __init__(self, master: tk.Misc, centrality_keys):
        super().__init__(master, padding=(10, 10, 10, 6))

        ttk.Label(self, text="Graph TSV file").grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        self.file_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.file_var, width=60, style="Tall.TEntry").grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        self.browse_button = ttk.Button(self, text="Browse", style="Tall.TButton")
        self.browse_button.grid(row=0, column=2, padx=4, pady=4, sticky=tk.W)

        ttk.Label(self, text="Edge 1 column").grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        self.edge1_var = tk.StringVar(value="edge1")
        ttk.Entry(self, textvariable=self.edge1_var, width=20, style="Tall.TEntry").grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)

        ttk.Label(self, text="Edge 2 column").grid(row=1, column=2, sticky=tk.W, padx=4, pady=4)
        self.edge2_var = tk.StringVar(value="edge2")
        ttk.Entry(self, textvariable=self.edge2_var, width=20, style="Tall.TEntry").grid(row=1, column=3, sticky=tk.W, padx=4, pady=4)

        ttk.Label(self, text="Weight column").grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        self.weight_var = tk.StringVar(value="weight")
        ttk.Entry(self, textvariable=self.weight_var, width=20, style="Tall.TEntry").grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)

        ttk.Label(self, text="Removed nodes (space-separated)").grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
        self.removed_nodes_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.removed_nodes_var, width=60, style="Tall.TEntry").grid(row=3, column=1, columnspan=3, sticky=tk.W, padx=4, pady=4)

        ttk.Label(self, text="Centrality measures").grid(row=4, column=0, sticky=tk.NW, padx=4, pady=4)
        self.centrality_vars = {}
        centralities_frame = ttk.Frame(self)
        centralities_frame.grid(row=4, column=1, columnspan=3, sticky=tk.W, padx=4, pady=4)
        for i, key in enumerate(centrality_keys):
            var = tk.BooleanVar(value=(key in ("degree", "betweenness", "closeness")))
            cb = ttk.Checkbutton(centralities_frame, text=key, variable=var)
            cb.grid(row=0, column=i, padx=4, pady=2, sticky=tk.W)
            self.centrality_vars[key] = var

        actions_frame = ttk.Frame(self)
        actions_frame.grid(row=5, column=0, columnspan=4, sticky=tk.W, padx=0, pady=(6, 0))
        self.run_button = ttk.Button(actions_frame, text="Run Analysis")
        self.run_button.pack(side=tk.LEFT, padx=(0, 6))
        self.save_button = ttk.Button(actions_frame, text="Save SVG As...")
        self.save_button.pack(side=tk.LEFT, padx=(0, 6))
        self.clear_button = ttk.Button(actions_frame, text="Clear")
        self.clear_button.pack(side=tk.LEFT)


class TableView(ttk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        columns = ("node", "new", "diff")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor=tk.W, stretch=True)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        try:
            self.tree.tag_configure('oddrow', background='#2a2d2e')
        except Exception:
            pass

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def populate(self, df: pd.DataFrame):
        self.clear()
        for idx, (node, row) in enumerate(df.iterrows()):
            import numpy as _np
            new_val = row.get("new", _np.nan)
            diff_val = row.get("diff", _np.nan)
            tag = 'oddrow' if idx % 2 else ''
            self.tree.insert("", tk.END, values=(str(node), f"{new_val:.6f}", f"{diff_val:.6f}"), tags=(tag,))


class PlotView(ttk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

    def clear(self):
        self.figure.clf()
        self.canvas.draw_idle()

    def draw_idle(self):
        self.canvas.draw_idle()


class StatusBarView(ttk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master, padding=(10, 6))
        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(self, textvariable=self.status_var).pack(side=tk.LEFT)

    def set_status(self, text: str):
        self.status_var.set(text)


class GraphAnalysisGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Graph Node Removal Analysis")
        self.geometry("1100x700")

        self._init_style()
        self._build_widgets()

        # cache for layouts used by plot_result
        self.pos_cache = {}
        self.last_save_dir = "."

        # Wire controller after widgets exist
        self._controller = GraphAnalysisController(self)

    def _init_style(self):
        style = ttk.Style(self)
        # Prefer a modern built-in theme as base
        try:
            style.theme_use("clam")
        except Exception:
            pass
        # Dark palette
        bg = "#1e1e1e"           # window background
        panel_bg = "#252526"      # panels
        fg = "#dddddd"            # text
        subtle = "#2d2d30"        # alternating rows / borders
        accent = "#0e639c"        # buttons / focus

        self.configure(background=bg)

        style.configure("TFrame", background=bg)
        style.configure("TPanedwindow", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TButton", background=panel_bg, foreground=fg, padding=(10, 6))
        style.map("TButton", background=[("active", "#3a3d41")])

        # Taller controls to align heights
        style.configure("Tall.TEntry", fieldbackground=panel_bg, foreground=fg, padding=(10, 6))
        style.configure("Tall.TButton", background=panel_bg, foreground=fg, padding=(10, 6))

        # Entry colors (ttk uses system, set through layout options)
        style.configure("TEntry", fieldbackground=panel_bg, foreground=fg)

        # Treeview dark styling
        style.configure(
            "Treeview",
            background=panel_bg,
            fieldbackground=panel_bg,
            foreground=fg,
            rowheight=24,
            font=("Segoe UI", 10),
            bordercolor=subtle,
            lightcolor=subtle,
            darkcolor=subtle,
        )
        style.configure("Treeview.Heading", background=subtle, foreground=fg, font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#094771")], foreground=[("selected", "#ffffff")])

        # Paned sash
        style.configure("Sash", background=subtle)


    def _build_widgets(self):
        # Top toolbar
        self.toolbar = ToolbarView(self, list(centrality_functions.keys()))
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.toolbar.browse_button.configure(command=self._browse_file)
        self.toolbar.run_button.configure(command=self._on_run)
        self.toolbar.save_button.configure(command=self._on_save_as)
        self.toolbar.clear_button.configure(command=self._on_clear)

        # Split view: resizable panes
        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Table
        self.table = TableView(paned)
        paned.add(self.table, weight=1)

        # Plot area
        self.plot = PlotView(paned)
        paned.add(self.plot, weight=1)

        # Status bar
        self.status = StatusBarView(self)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def _browse_file(self):
        path = filedialog.askopenfilename(title="Select graph TSV", filetypes=[("TSV files", "*.tsv"), ("All files", "*.*")])
        if path:
            self.toolbar.file_var.set(path)

    def _on_run(self):
        # run in background to keep UI responsive
        thread = threading.Thread(target=self._run_analysis_safe)
        thread.daemon = True
        thread.start()

    def _on_save_as(self):
        try:
            path = filedialog.asksaveasfilename(
                title="Save SVG",
                defaultextension=".svg",
                filetypes=[("SVG", "*.svg")],
                initialdir=self.last_save_dir,
                initialfile="Read from TSV.svg",
            )
            if not path:
                return
            import os
            self.last_save_dir = os.path.dirname(path)
            # Use plot_result to save to selected folder; it names file by label
            # So we pass save_path to the directory and then rename if needed
            file_path = self.toolbar.file_var.get().strip()
            if not file_path:
                messagebox.showwarning("Save SVG", "Run an analysis first.")
                return
            # Recreate and save latest plot based on last computed data by rerunning lightweight save
            # We call _run_analysis but that also computes; instead, save current figure to path
            self.plot.figure.savefig(path, dpi=300, bbox_inches='tight', facecolor='white', format='svg')
            self.status.set_status(f"Saved: {path}")
        except Exception as e:
            messagebox.showerror("Save SVG", str(e))

    def _on_clear(self):
        self.table.clear()
        self.plot.clear()
        self.status.set_status("Cleared")

    def _run_analysis_safe(self):
        try:
            self.status.set_status("Running analysis...")
            self._run_analysis()
            self.status.set_status("Done")
        except Exception as e:
            self.status.set_status("Error")
            messagebox.showerror("Error", str(e))

    def _run_analysis(self):
        # Delegate to controller for separation of concerns
        self._controller.run_analysis()

    def _populate_table(self, df: pd.DataFrame):
        # kept for backward compatibility if called; delegate to TableView
        self.table.populate(df)

    
class GraphLoader:
    def load(self, edge1: str, edge2: str, weight: str, path: str) -> nx.Graph:
        import networkx as nx
        # read file
        df = pd.read_csv(path, sep="\t")
        # build undirected graph
        G = nx.Graph()
        for _, row in df.iterrows():
            if row[edge1] == row[edge2]:
                continue
            G.add_edge(row[edge1], row[edge2], weight=row[weight])
        return G


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


class LayoutCache:
    def __init__(self):
        self._cache = {}

    def get(self, key) -> Optional[dict[Any, tuple[float, float]]]:
        return self._cache.get(key)

    def set(self, key, value) -> None:
        self._cache[key] = value


class PlotRenderer:
    def __init__(self, layout_cache: LayoutCache):
        self.layout_cache = layout_cache

    def render(self, figure: Figure, result: dict[str, Any]) -> None:
        from matplotlib import cm, colors
        import networkx as nx

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

        # Build edge lists and widths aligned to edges
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


class GraphAnalysisController:
    def __init__(self, app: GraphAnalysisGUI):
        self.app = app
        self.loader = GraphLoader()
        self.analysis = CentralityAnalysisService()
        self.layout_cache = LayoutCache()
        self.renderer = PlotRenderer(self.layout_cache)

    def run_analysis(self) -> None:
        file_path = self.app.toolbar.file_var.get().strip()
        edge1 = self.app.toolbar.edge1_var.get().strip() or "edge1"
        edge2 = self.app.toolbar.edge2_var.get().strip() or "edge2"
        weight = self.app.toolbar.weight_var.get().strip() or "weight"
        removed_nodes = [n for n in self.app.toolbar.removed_nodes_var.get().split() if n]
        selected_cents = [k for k, v in self.app.toolbar.centrality_vars.items() if v.get()]

        if not file_path:
            raise ValueError("Please select a TSV file")
        if not removed_nodes:
            raise ValueError("Please enter at least one removed node")
        if not selected_cents:
            raise ValueError("Please select at least one centrality measure")

        G = self.loader.load(edge1, edge2, weight, file_path)
        df, impact = self.analysis.compute(G, removed_nodes, selected_cents)

        # Update table on UI thread
        self.app.after(0, lambda: self.app.table.populate(df))

        # Render plot
        result = {
            "label": "Read from TSV",
            "gtype": "Read from TSV",
            "impact": impact,
            "graph": G,
            "removed_nodes": removed_nodes,
        }
        self.renderer.render(self.app.plot.figure, result)
        self.app.plot.draw_idle()


def main() -> None:
    app = GraphAnalysisGUI()
    app.mainloop()


if __name__ == "__main__":
    main()


