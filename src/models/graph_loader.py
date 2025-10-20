import pandas as pd
import networkx as nx
import zipfile
import os
import networkxgmml

class GraphLoader:
    def load(self, edge1: str, edge2: str, weight: str, path: str, remove_self_edges: bool = True, network_name: str = None) -> nx.Graph:
        """
        Load a graph from either a TSV file or a Cytoscape .cys file.

        Args:
            edge1: Column name for source node (used for TSV files)
            edge2: Column name for target node (used for TSV files)
            weight: Column name for edge weight (used for TSV files)
            path: Path to the file (either .tsv or .cys)
            remove_self_edges: Whether to remove self-edges
            network_name: Name of the network to load from .cys file (optional, defaults to first network)

        Returns:
            A NetworkX Graph object
        """
        file_ext = os.path.splitext(path)[1].lower()

        if file_ext == '.cys':
            return self._load_cys(path, remove_self_edges, network_name)
        else:
            # Default to TSV loading for .tsv or other files
            return self._load_tsv(edge1, edge2, weight, path, remove_self_edges)

    def _load_tsv(self, edge1: str, edge2: str, weight: str, path: str, remove_self_edges: bool = True) -> nx.Graph:
        """Load graph from TSV file."""
        df = pd.read_csv(path, sep="\t")
        G = nx.Graph()
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
                # Parse XGMML using networkxgmml
                G_directed = networkxgmml.XGMMLReader(xgmml_content)

                # Convert to undirected graph (as the original code uses nx.Graph())
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
                            weight = 1.0
                    else:
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


