from typing import Any


class GraphAnalysisController:
    def __init__(self, app: Any, loader, analysis, layout_cache, renderer):
        self.app = app
        self.loader = loader
        self.analysis = analysis
        self.layout_cache = layout_cache
        self.renderer = renderer

    def generate_preview(self) -> None:
        file_path = self.app.toolbar.file_var.get().strip()
        edge1 = self.app.toolbar.edge1_var.get().strip()
        edge2 = self.app.toolbar.edge2_var.get().strip()
        weight = self.app.toolbar.weight_var.get().strip()
        remove_self_edges = self.app.toolbar.remove_self_edges_var.get()

        # Check if file is .cys or TSV
        import os
        file_ext = os.path.splitext(file_path)[1].lower() if file_path else ""

        # For .cys files, we don't need column specifications
        if file_ext == '.cys':
            if not file_path:
                return
        else:
            # For TSV files, we need all column specifications
            if not file_path or not edge1 or not edge2 or not weight:
                return

        try:
            self.app.status.set_status("Loading preview...")
            G = self.loader.load(edge1, edge2, weight, file_path, remove_self_edges)

            preview_result = {
                "label": "Graph Preview",
                "gtype": "Preview",
                "impact": {},  # Empty impact for preview
                "graph": G,
                "removed_nodes": [],  # No removed nodes in preview
            }

            preview_options = {
                "show_node_names": True,
                "edge_thickness_by_weight": True,
                "mark_removed_edges": False,
            }

            self.renderer.render(self.app.plot.figure, preview_result, preview_options)
            self.app.plot.canvas.draw()

            self.app.status.set_status(f"Preview loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

        except Exception as e:
            self.app.status.set_status(f"Preview failed: {str(e)}")
            import traceback
            traceback.print_exc()

    def run_analysis(self) -> None:
        file_path = self.app.toolbar.file_var.get().strip()
        edge1 = self.app.toolbar.edge1_var.get().strip() or "edge1"
        edge2 = self.app.toolbar.edge2_var.get().strip() or "edge2"
        weight = self.app.toolbar.weight_var.get().strip() or "weight"
        removed_nodes = [n for n in self.app.toolbar.removed_nodes_var.get().split() if n]
        selected_cents = [k for k, v in self.app.toolbar.centrality_vars.items() if v.get()]
        remove_self_edges = self.app.toolbar.remove_self_edges_var.get()

        if not file_path:
            raise ValueError("Please select a graph file")
        if not removed_nodes:
            raise ValueError("Please enter at least one removed node")
        if not selected_cents:
            raise ValueError("Please select at least one centrality measure")

        G = self.loader.load(edge1, edge2, weight, file_path, remove_self_edges)
        df, impact = self.analysis.compute(G, removed_nodes, selected_cents)

        self.app.after(0, lambda: self.app.table.populate(df))

        # Determine file type for label
        import os
        file_ext = os.path.splitext(file_path)[1].lower()
        file_type = "CYS" if file_ext == '.cys' else "TSV"

        result = {
            "label": f"Read from {file_type}",
            "gtype": f"Read from {file_type}",
            "impact": impact,
            "graph": G,
            "removed_nodes": removed_nodes,
        }

        # Store the result for later refresh
        self.app.last_analysis_result = result

        # Get current plot options
        plot_options = {
            "show_node_names": self.app.toolbar.show_node_names_var.get(),
            "edge_thickness_by_weight": self.app.toolbar.edge_thickness_by_weight_var.get(),
            "mark_removed_edges": self.app.toolbar.mark_removed_edges_var.get(),
        }

        self.renderer.render(self.app.plot.figure, result, plot_options)


