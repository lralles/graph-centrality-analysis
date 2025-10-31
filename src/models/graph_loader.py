import pandas as pd
import networkx as nx
import zipfile
import os
import networkxgmml

class GraphLoader:
    def load(self, edge1: str, edge2: str, weight: str, path: str, remove_self_edges: bool = True, network_name: str = None, directed: bool = False) -> nx.Graph:
        """
        Load a graph from a TSV file, a Cytoscape .cys file, or a GEXF file.

        Args:
            edge1: Column name for source node (used for TSV files)
            edge2: Column name for target node (used for TSV files)
            weight: Column name for edge weight (used for TSV files)
            path: Path to the file (either .tsv, .cys, or .gexf)
            remove_self_edges: Whether to remove self-edges
            network_name: Name of the network to load from .cys file (optional, defaults to first network)
            directed: Whether to create a directed graph (default: False for undirected)

        Returns:
            A NetworkX Graph or DiGraph object
        """
        file_ext = os.path.splitext(path)[1].lower()

        if file_ext == '.cys':
            return self._load_cys(path, remove_self_edges, network_name)
        elif file_ext == '.gexf':
            return self._load_gexf(path, remove_self_edges, directed)
        else:
            # Default to TSV loading for .tsv or other files
            return self._load_tsv(edge1, edge2, weight, path, remove_self_edges, directed)

    def _load_gexf(self, path: str, remove_self_edges: bool = True, directed: bool = False) -> nx.Graph:
        """
        Load a graph from a GEXF file.

        This reads the GEXF using NetworkX and optionally converts the graph
        to directed/undirected based on the `directed` flag. It also removes
        self-edges if requested.
        """
        G = nx.read_gexf(path)

        # Ensure graph directedness matches the requested flag
        if directed and not G.is_directed():
            G = G.to_directed()
        elif not directed and G.is_directed():
            G = G.to_undirected()

        # Remove self-edges if requested
        if remove_self_edges:
            self_edges = [(u, v) for u, v in G.edges() if u == v]
            if self_edges:
                G.remove_edges_from(self_edges)

        return G

    def _load_tsv(self, edge1: str, edge2: str, weight: str, path: str, remove_self_edges: bool = True, directed: bool = False) -> nx.Graph:
        """Load graph from TSV file."""
        df = pd.read_csv(path, sep="\t")
        G = nx.DiGraph() if directed else nx.Graph()
        for _, row in df.iterrows():
            if remove_self_edges and row[edge1] == row[edge2]:
                continue
            G.add_edge(row[edge1], row[edge2], weight=row[weight])
        return G

    def _load_cys(self, path: str, remove_self_edges: bool = True, network_name: str = None) -> nx.Graph:
        """
        Load graph from Cytoscape .cys file.

        A .cys file is a ZIP archive containing XGMML files.
        This method extracts the specified XGMML file (or the first one if not specified) and loads it.

        Args:
            path: Path to the .cys file
            remove_self_edges: Whether to remove self-edges
            network_name: Name of the network (XGMML file) to load. If None, loads the first network.
        """
        with zipfile.ZipFile(path, 'r') as zip_ref:
            # Find all XGMML files in the archive
            xgmml_files = [f for f in zip_ref.namelist() if f.endswith('.xgmml')]

            if not xgmml_files:
                raise ValueError("No XGMML files found in the .cys archive")

            # Select the XGMML file to load
            if network_name:
                # Find the file matching the network name
                xgmml_file = None
                for f in xgmml_files:
                    if os.path.basename(f) == network_name:
                        xgmml_file = f
                        break
                if not xgmml_file:
                    raise ValueError(f"Network '{network_name}' not found in .cys file. Available networks: {[os.path.basename(f) for f in xgmml_files]}")
            else:
                # Use the first XGMML file found
                xgmml_file = xgmml_files[0]

            # Extract and read the XGMML file
            with zip_ref.open(xgmml_file) as xgmml_content:
                G_directed = networkxgmml.XGMMLReader(xgmml_content)
                G = nx.Graph()

                # Create a mapping from original node IDs to labels (node names)
                id_to_label = {}

                # Copy nodes with their attributes, using labels as node identifiers
                for node_id, attrs in G_directed.nodes(data=True):
                    # Use the label as the node name if available, otherwise use the ID
                    node_name = attrs.get('label', node_id)
                    id_to_label[node_id] = node_name
                    G.add_node(node_name, **attrs)

                # Copy edges with their attributes, mapping IDs to labels
                for source_id, target_id, attrs in G_directed.edges(data=True):
                    source_name = id_to_label[source_id]
                    target_name = id_to_label[target_id]

                    if remove_self_edges and source_name == target_name:
                        continue

                    # Extract weight from the 'interaction' attribute if available
                    weight = None
                    if 'interaction' in attrs:
                        try:
                            weight = float(attrs['interaction'])
                        except (ValueError, TypeError):
                            # Try other numeric attributes if 'interaction' couldn't be parsed
                            weight = None
                            for key in ('weight', 'score', 'value'):
                                val = attrs.get(key)
                                if val not in (None, ''):
                                    try:
                                        weight = float(val)
                                        break
                                    except (ValueError, TypeError):
                                        weight = None
                            if weight is None:
                                weight = 1.0
                    else:
                        # No 'interaction' attribute; check common numeric fields before defaulting
                        weight = None
                        for key in ('weight', 'score', 'value'):
                            val = attrs.get(key)
                            if val not in (None, ''):
                                try:
                                    weight = float(val)
                                    break
                                except (ValueError, TypeError):
                                    weight = None
                        if weight is None:
                            weight = 1.0

                    # Add edge with weight
                    G.add_edge(source_name, target_name, weight=weight, **attrs)

                return G

    def get_available_networks(self, path: str) -> list[str]:
        """
        Get list of available networks in a .cys file.

        Args:
            path: Path to the .cys file

        Returns:
            List of network names (XGMML file names)
        """
        if not path.endswith('.cys'):
            return []

        try:
            with zipfile.ZipFile(path, 'r') as zip_ref:
                xgmml_files = [f for f in zip_ref.namelist() if f.endswith('.xgmml')]
                # Extract just the filename without path
                return [os.path.basename(f) for f in xgmml_files]
        except Exception:
            return []


    def process_graph(self, G: nx.Graph, remove_zero_degree: bool = False, use_largest_component: bool = False) -> nx.Graph:
        """
        Apply graph processing operations.

        Args:
            G: Input graph
            remove_zero_degree: Whether to remove nodes with degree 0
            use_largest_component: Whether to keep only the largest connected component

        Returns:
            Processed graph
        """
        # Create a copy to avoid modifying the original
        processed_G = G.copy()

        # Remove zero degree nodes
        if remove_zero_degree:
            processed_G = self._remove_zero_degree_nodes(processed_G)

        # Use only largest component
        if use_largest_component:
            processed_G = self._extract_largest_component(processed_G)

        return processed_G

    def _remove_zero_degree_nodes(self, G: nx.Graph) -> nx.Graph:
        """
        Remove all nodes with degree 0 from the graph.

        Args:
            G: Input graph

        Returns:
            Graph with zero degree nodes removed
        """
        # Find nodes with degree 0
        zero_degree_nodes = [node for node, degree in G.degree() if degree == 0]

        # Remove them from the graph
        G.remove_nodes_from(zero_degree_nodes)

        return G

    def _extract_largest_component(self, G: nx.Graph) -> nx.Graph:
        """
        Extract the largest connected component from the graph.

        Args:
            G: Input graph

        Returns:
            Subgraph containing only the largest connected component
        """
        if G.is_directed():
            # For directed graphs, use weakly connected components
            components = list(nx.weakly_connected_components(G))
        else:
            # For undirected graphs, use connected components
            components = list(nx.connected_components(G))

        if not components:
            return G

        # Find the largest component
        largest_component = max(components, key=len)

        # Return subgraph with only the largest component
        return G.subgraph(largest_component).copy()


    def export_cys(self, graph: nx.Graph, output_path: str, network_name: str = "network",
                   combined_centrality: dict = None, combined_delta: dict = None) -> None:
        """
        Export a NetworkX graph as a Cytoscape .cys file with additional node attributes.

        Args:
            graph: NetworkX graph to export
            output_path: Path where to save the .cys file
            network_name: Name for the network (default: "network")
            combined_centrality: Dictionary mapping node names to combined centrality values
            combined_delta: Dictionary mapping node names to combined delta values
        """
        import os
        import zipfile
        import tempfile

        # Create a copy of the graph to avoid modifying the original
        export_graph = graph.copy()

        # Add combined centrality and delta attributes to nodes if provided
        if combined_centrality:
            for node in export_graph.nodes():
                if node in combined_centrality:
                    export_graph.nodes[node]['Combined Centrality'] = combined_centrality[node]

        if combined_delta:
            for node in export_graph.nodes():
                if node in combined_delta:
                    export_graph.nodes[node]['Combined Delta'] = combined_delta[node]

        # Create a temporary directory for the XGMML file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate XGMML filename
            xgmml_filename = f"{network_name}.xgmml"
            xgmml_path = os.path.join(temp_dir, xgmml_filename)

            # Prefer networkxgmml if available, otherwise fall back to NetworkX writers
            try:
                import networkxgmml
                networkxgmml.XGMMLWriter(export_graph, xgmml_path)
            except Exception:
                # Fallback: write GraphML (keeps node attributes) or GEXF if GraphML fails
                try:
                    import networkx as nx
                    nx.write_graphml(export_graph, xgmml_path)
                except Exception:
                    # As a last resort use GEXF
                    nx.write_gexf(export_graph, xgmml_path)

            # Create the .cys file (ZIP archive)
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                zip_ref.write(xgmml_path, xgmml_filename)


