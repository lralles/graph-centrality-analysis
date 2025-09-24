from typing import Any


class GraphAnalysisController:
    def __init__(self, app: Any, loader, analysis, layout_cache, renderer):
        self.app = app
        self.loader = loader
        self.analysis = analysis
        self.layout_cache = layout_cache
        self.renderer = renderer

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

        self.app.after(0, lambda: self.app.table.populate(df))

        result = {
            "label": "Read from TSV",
            "gtype": "Read from TSV",
            "impact": impact,
            "graph": G,
            "removed_nodes": removed_nodes,
        }
        self.renderer.render(self.app.plot.figure, result)
        self.app.plot.draw_idle()


