import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from read_file import read_file
from node_removal_graph_analyser import get_node_removal_impact, centrality_functions
from graph_plot import plot_result


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
        toolbar = ttk.Frame(self, padding=(10, 10, 10, 6))
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # File selection
        ttk.Label(toolbar, text="Graph TSV file").grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(toolbar, textvariable=self.file_var, width=60, style="Tall.TEntry")
        file_entry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        ttk.Button(toolbar, text="Browse", command=self._browse_file, style="Tall.TButton").grid(row=0, column=2, padx=4, pady=4, sticky=tk.W)

        # Edge columns
        ttk.Label(toolbar, text="Edge 1 column").grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        self.edge1_var = tk.StringVar(value="edge1")
        ttk.Entry(toolbar, textvariable=self.edge1_var, width=20, style="Tall.TEntry").grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)

        ttk.Label(toolbar, text="Edge 2 column").grid(row=1, column=2, sticky=tk.W, padx=4, pady=4)
        self.edge2_var = tk.StringVar(value="edge2")
        ttk.Entry(toolbar, textvariable=self.edge2_var, width=20, style="Tall.TEntry").grid(row=1, column=3, sticky=tk.W, padx=4, pady=4)

        # Weight column
        ttk.Label(toolbar, text="Weight column").grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        self.weight_var = tk.StringVar(value="weight")
        ttk.Entry(toolbar, textvariable=self.weight_var, width=20, style="Tall.TEntry").grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)

        # Removed nodes
        ttk.Label(toolbar, text="Removed nodes (space-separated)").grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
        self.removed_nodes_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.removed_nodes_var, width=60, style="Tall.TEntry").grid(row=3, column=1, columnspan=3, sticky=tk.W, padx=4, pady=4)

        # Centralities checklist
        ttk.Label(toolbar, text="Centrality measures").grid(row=4, column=0, sticky=tk.NW, padx=4, pady=4)
        self.centrality_vars = {}
        centralities_frame = ttk.Frame(toolbar)
        centralities_frame.grid(row=4, column=1, columnspan=3, sticky=tk.W, padx=4, pady=4)
        for i, key in enumerate(centrality_functions.keys()):
            var = tk.BooleanVar(value=(key in ("degree", "betweenness", "closeness")))
            cb = ttk.Checkbutton(centralities_frame, text=key, variable=var)
            cb.grid(row=0, column=i, padx=4, pady=2, sticky=tk.W)
            self.centrality_vars[key] = var

        # Action buttons
        actions_frame = ttk.Frame(toolbar)
        actions_frame.grid(row=5, column=0, columnspan=4, sticky=tk.W, padx=0, pady=(6, 0))
        ttk.Button(actions_frame, text="Run Analysis", command=self._on_run).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(actions_frame, text="Save SVG As...", command=self._on_save_as).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(actions_frame, text="Clear", command=self._on_clear).pack(side=tk.LEFT)

        # Split view: resizable panes
        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Table
        table_container = ttk.Frame(paned)
        paned.add(table_container, weight=1)
        columns = ("node", "new", "diff")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor=tk.W, stretch=True)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # zebra striping tag
        try:
            self.tree.tag_configure('oddrow', background='#2a2d2e')
        except Exception:
            pass

        # Plot area
        plot_frame = ttk.Frame(paned)
        paned.add(plot_frame, weight=1)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Status bar
        status_bar = ttk.Frame(self, padding=(10, 6))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(status_bar, textvariable=self.status_var).pack(side=tk.LEFT)

    def _browse_file(self):
        path = filedialog.askopenfilename(title="Select graph TSV", filetypes=[("TSV files", "*.tsv"), ("All files", "*.*")])
        if path:
            self.file_var.set(path)

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
            file_path = self.file_var.get().strip()
            if not file_path:
                messagebox.showwarning("Save SVG", "Run an analysis first.")
                return
            # Recreate and save latest plot based on last computed data by rerunning lightweight save
            # We call _run_analysis but that also computes; instead, save current figure to path
            self.figure.savefig(path, dpi=300, bbox_inches='tight', facecolor='white', format='svg')
            self.status_var.set(f"Saved: {path}")
        except Exception as e:
            messagebox.showerror("Save SVG", str(e))

    def _on_clear(self):
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Clear plot
        self.figure.clf()
        self.canvas.draw_idle()
        self.status_var.set("Cleared")

    def _run_analysis_safe(self):
        try:
            self.status_var.set("Running analysis...")
            self._run_analysis()
            self.status_var.set("Done")
        except Exception as e:
            self.status_var.set("Error")
            messagebox.showerror("Error", str(e))

    def _run_analysis(self):
        file_path = self.file_var.get().strip()
        edge1 = self.edge1_var.get().strip() or "edge1"
        edge2 = self.edge2_var.get().strip() or "edge2"
        weight = self.weight_var.get().strip() or "weight"
        removed_nodes = [n for n in self.removed_nodes_var.get().split() if n]
        selected_cents = [k for k, v in self.centrality_vars.items() if v.get()]

        if not file_path:
            raise ValueError("Please select a TSV file")
        if not removed_nodes:
            raise ValueError("Please enter at least one removed node")
        if not selected_cents:
            raise ValueError("Please select at least one centrality measure")

        # read file
        G = read_file(edge1, edge2, weight, file_path)

        # accumulate deltas and scores like CLI
        overall_centrality_delta = {}
        overall_centrality_score = {}

        for centrality in selected_cents:
            _, node_removal_impact, new_centrality = get_node_removal_impact(
                G, removed_nodes, centrality_functions[centrality]
            )

            for k, v in node_removal_impact.items():
                overall_centrality_delta[k] = overall_centrality_delta.get(k, 0) + v

            for k, v in new_centrality.items():
                overall_centrality_score[k] = overall_centrality_score.get(k, 0) + v

        # Build dataframe
        centrality_table = {}
        for node in overall_centrality_score:
            new_val = overall_centrality_score[node]
            diff = overall_centrality_delta.get(node, np.nan)
            centrality_table[node] = {"new": new_val, "diff": diff}

        df = pd.DataFrame.from_dict(centrality_table, orient="index")

        # update table in UI thread
        self.after(0, lambda: self._populate_table(df))

        # render and save SVG using existing plot_result
        result = {
            "label": "Read from TSV",
            "gtype": "Read from TSV",
            "impact": overall_centrality_delta,
            "graph": G,
            "removed_nodes": removed_nodes,
        }

        # Save SVG to current directory and also draw in Tk canvas
        plot_result(result, self.pos_cache, save_plots=True, showLabels=True, save_path=".")

        # draw into Tk canvas
        self._draw_matplotlib_graph(result)

    def _populate_table(self, df: pd.DataFrame):
        # clear
        for item in self.tree.get_children():
            self.tree.delete(item)

        # insert
        for idx, (node, row) in enumerate(df.iterrows()):
            new_val = row.get("new", np.nan)
            diff_val = row.get("diff", np.nan)
            tag = 'oddrow' if idx % 2 else ''
            self.tree.insert("", tk.END, values=(str(node), f"{new_val:.6f}", f"{diff_val:.6f}"), tags=(tag,))

    def _draw_matplotlib_graph(self, result):
        # clear previous figure
        self.figure.clf()
        ax = self.figure.add_subplot(111)

        # Recreate a minimal plot similar to plot_result for embedding
        # We do not save here; just display
        from matplotlib import cm, colors
        import networkx as nx

        G = result["graph"]
        impact = result["impact"]
        removed_nodes = result["removed_nodes"]
        size = G.number_of_nodes()

        key = (result["gtype"], size)
        if key not in self.pos_cache:
            if size >= 500:
                self.pos_cache[key] = nx.spring_layout(G, seed=42, k=1 / np.sqrt(size))
            else:
                self.pos_cache[key] = nx.spring_layout(G, seed=42)
        pos = self.pos_cache[key]

        max_abs = max((abs(v) for v in impact.values()), default=0.0)
        if max_abs == 0:
            norm = colors.TwoSlopeNorm(vmin=-1.0, vcenter=0.0, vmax=1.0)
        else:
            norm = colors.TwoSlopeNorm(vmin=-max_abs, vcenter=0.0, vmax=max_abs)

        cmap = matplotlib.pyplot.get_cmap("bwr")
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

        # edge widths from weights
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

        import networkx as nx
        nx.draw(
            G,
            pos,
            node_color=node_colors,
            node_size=node_size,
            edge_color="lightgrey",
            width=edge_widths,
            ax=ax,
            with_labels=True,
            linewidths=0.8,
            edgecolors="black",
        )
        ax.set_title(result["label"])

        # draw colorbar
        sm = matplotlib.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        self.figure.colorbar(sm, ax=ax, fraction=0.04, pad=0.05).set_label("Δ centrality")

        self.canvas.draw_idle()


def main():
    app = GraphAnalysisGUI()
    app.mainloop()


if __name__ == "__main__":
    main()


