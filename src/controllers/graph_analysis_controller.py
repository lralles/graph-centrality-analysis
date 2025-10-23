from os import path

from typing import Any

class GraphAnalysisController:
    def __init__(self, app: Any, loader, analysis, layout_cache, renderer):
        self.app = app
        self.loader = loader
        self.analysis = analysis
        self.layout_cache = layout_cache
        self.renderer = renderer
        self.random_graph = None  # Store random graph when generated
    def set_random_graph(self, graph):
        """Set a random graph for analysis"""
        self.random_graph = graph

    def generate_preview(self) -> None:
        """
        Generates the graph preview if the graph can be loaded
        """
        # Check if we're in random graph mode
        if self.app.toolbar.is_random_graph_mode():
            if self.random_graph is None:
                return

            try:
                self.app.status.set_status("Loading preview...")
                G = self.random_graph.copy()  # Make a copy to avoid modifying the original

                # Apply graph processing options
                remove_zero_degree = self.app.toolbar.remove_zero_degree_var.get()
                use_largest_component = self.app.toolbar.use_largest_component_var.get()
                G = self.loader.process_graph(G, remove_zero_degree, use_largest_component)

                # uses the same visualization engine as the impact, but with different options
                preview_result = {
                    "label": "Graph Preview",
                    "gtype": "Preview",
                    "impact": {},           # Empty impact for preview
                    "graph": G,
                    "removed_nodes": [],    # No removed nodes in preview
                }

                preview_options = {
                    "show_node_names": True,
                    "edge_thickness_by_weight": True,
                    "mark_removed_edges": False,
                }

                self.renderer.render(self.app.plot.figure, preview_result, preview_options)
                self.app.plot.canvas.draw()

                self.app.status.set_status(f"Preview loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

                # Populate the node selector with available nodes
                nodes = sorted(G.nodes())
                self.app.toolbar.update_node_list(nodes)

                # Populate the adjacency list and show it
                self.app.adjacency_list.populate(G)
                self.app._show_adjacency_list()

            except Exception as e:
                self.app.status.set_status(f"Preview failed: {str(e)}")
            return

        # Original file-based preview logic
        file_path = self.app.toolbar.file_var.get().strip()
        if not file_path:
            return

        edge1 = self.app.toolbar.edge1_var.get().strip()
        edge2 = self.app.toolbar.edge2_var.get().strip()
        weight = self.app.toolbar.weight_var.get().strip()
        remove_self_edges = self.app.toolbar.remove_self_edges_var.get()
        directed = self.app.toolbar.directed_graph_var.get()
        network_name = self.app.toolbar.get_selected_network()

        # Check if file is TSV, if is and graph info is not available, skip
        file_ext = path.splitext(file_path)[1].lower() if file_path else ""
        if file_ext == ".tsv":
            if not file_path or not edge1 or not edge2 or not weight:
                return

        try:
            self.app.status.set_status("Loading preview...")
            G = self.loader.load(edge1, edge2, weight, file_path, remove_self_edges, network_name, directed)

            # Apply graph processing options
            remove_zero_degree = self.app.toolbar.remove_zero_degree_var.get()
            use_largest_component = self.app.toolbar.use_largest_component_var.get()
            G = self.loader.process_graph(G, remove_zero_degree, use_largest_component)

            # uses the same visualization engine as the impact, but with different options
            preview_result = {
                "label": "Graph Preview",
                "gtype": "Preview",
                "impact": {},           # Empty impact for preview
                "graph": G,
                "removed_nodes": [],    # No removed nodes in preview
            }

            preview_options = {
                "show_node_names": True,
                "edge_thickness_by_weight": True,
                "mark_removed_edges": False,
            }

            self.renderer.render(self.app.plot.figure, preview_result, preview_options)
            self.app.plot.canvas.draw()

            self.app.status.set_status(f"Preview loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

            # Populate the node selector with available nodes
            nodes = sorted(G.nodes())
            self.app.toolbar.update_node_list(nodes)

            # Populate the adjacency list and show it
            self.app.adjacency_list.populate(G)
            self.app._show_adjacency_list()

        except Exception as e:
            self.app.status.set_status(f"Preview failed: {str(e)}")

    def run_analysis(self) -> None:
        """
        Runs the centrality analysis
        Populates the table
        Plots the result in the graph view
        """
        # Get the selected nodes from the toolbar (these may be strings)
        removed_nodes_str = self.app.toolbar.get_selected_nodes()
        selected_centralities = [k for k, v in self.app.toolbar.centrality_vars.items() if v.get()]

        if not removed_nodes_str:
            raise ValueError("Please select at least one node to remove")
        if not selected_centralities:
            raise ValueError("Please select at least one centrality measure")

        # Handle random graph mode
        if self.app.toolbar.is_random_graph_mode():
            if self.random_graph is None:
                raise ValueError("Please generate a random graph first")

            G = self.random_graph.copy()  # Make a copy to avoid modifying the original

            # Convert string node IDs back to the original type (int for random graphs)
            removed_nodes = []
            for node_str in removed_nodes_str:
                try:
                    # Try to convert to int first (for random graphs)
                    removed_nodes.append(int(node_str))
                except ValueError:
                    # If conversion fails, keep as string
                    removed_nodes.append(node_str)

            params = self.app.toolbar.get_random_graph_params()
            from src.models.random_graph_generator import get_graph_type_display_names
            display_names = get_graph_type_display_names()
            graph_type_display = display_names.get(params['graph_type'], params['graph_type'])
            file_type = f"Random {graph_type_display}"
        else:
            # Handle file-based mode
            file_path = self.app.toolbar.file_var.get().strip()
            edge1 = self.app.toolbar.edge1_var.get().strip() or "edge1"
            edge2 = self.app.toolbar.edge2_var.get().strip() or "edge2"
            weight = self.app.toolbar.weight_var.get().strip() or "weight"
            remove_self_edges = self.app.toolbar.remove_self_edges_var.get()
            directed = self.app.toolbar.directed_graph_var.get()
            network_name = self.app.toolbar.get_selected_network()

            if not file_path:
                raise ValueError("Please select a graph file")

            G = self.loader.load(edge1, edge2, weight, file_path, remove_self_edges, network_name, directed)

            # For file-based graphs, keep nodes as strings (they're usually strings anyway)
            removed_nodes = removed_nodes_str

        # Apply graph processing options to both random and file-based graphs
        remove_zero_degree = self.app.toolbar.remove_zero_degree_var.get()
        use_largest_component = self.app.toolbar.use_largest_component_var.get()
        G = self.loader.process_graph(G, remove_zero_degree, use_largest_component)
        file_type = f"Read from {file_type}"

        df, impact, diameter_info = self.analysis.compute(G, removed_nodes, selected_centralities)

        # Switch to analysis table view and populate it
        self.app._show_analysis_table()
        self.app.table.populate(df)

        # Update diameter display if available
        try:
            if isinstance(diameter_info, dict):
                before = diameter_info.get('before')
                after = diameter_info.get('after')
                if before is not None and after is not None:
                    self.app.table.update_diameter_display(before, after)
        except Exception:
            # Don't let diameter display issues break the analysis flow
            pass

        # Create a readable list of removed nodes
        removed_nodes_str = ", ".join(str(node) for node in removed_nodes)

        result = {
            "label": f"Removed Nodes: {removed_nodes_str}",
            "gtype": file_type,
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
            "layout_type": self.app.toolbar.layout_type_var.get(),
        }

        self.renderer.render(self.app.plot.figure, result, plot_options)

