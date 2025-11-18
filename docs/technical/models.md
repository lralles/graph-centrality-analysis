# Models Documentation

The model layer handles data management, graph processing, and analysis computations.

## GraphLoader (`graph_loader.py`)

**Purpose**: Loads graphs from various file formats

**Dependencies**: 
- `pandas`, `networkx`, `networkxgmml`
- File system access

**Key Methods**:
- `load()`: Main entry point for loading graphs from TSV, CYS, or GEXF files
- `_load_tsv()`: Loads edge lists from tab-separated files
- `_load_cys()`: Extracts networks from Cytoscape session files
- `_load_gexf()`: Loads GEXF format files
- `process_graph()`: Applies filtering (zero-degree nodes, largest component)
- `get_networks_from_cys()`: Lists available networks in CYS files

## CentralityAnalysisService (`centrality_service.py`)

**Purpose**: Performs centrality analysis and node removal impact calculations

**Dependencies**: 
- `networkx`, `numpy`, `pandas`
- Centrality algorithms from NetworkX

**Key Methods**:
- `get_node_removal_impact()`: Calculates centrality changes after node removal
- `centrality_functions`: Dictionary mapping centrality names to NetworkX functions

**Available Centralities**:
- Degree, Betweenness, Closeness, Eigenvector, Katz

## LayoutCache (`layout_cache.py`)

**Purpose**: Caches graph layout positions to maintain consistency across visualizations

**Dependencies**: 
- `networkx` layout algorithms
- Memory storage

**Key Methods**:
- `get_layout()`: Retrieves or computes graph layout positions
- `clear_cache()`: Removes cached layouts
- `_compute_layout()`: Generates new layout using specified algorithm

## RandomGraphGenerator (`random_graph_generator.py`)

**Purpose**: Generates various types of random graphs for testing and demonstration

**Dependencies**: 
- `networkx` graph generators

**Key Methods**:
- `generate_erdos_renyi()`: Random graphs with fixed edge probability
- `generate_barabasi_albert()`: Scale-free networks
- `generate_watts_strogatz()`: Small-world networks