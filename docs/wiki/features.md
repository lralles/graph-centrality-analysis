# Features

The Graph Centrality Analysis application provides comprehensive tools for analyzing network structure and node importance.

## Graph Loading

### File Support
- **TSV/CSV**: Tab or comma-separated edge lists
- **CYS**: Cytoscape session files with multiple networks
- **GEXF**: Standard graph exchange format

### Random Graph Generation
- **Erdős-Rényi**: Random graphs with fixed edge probability
- **Barabási-Albert**: Scale-free networks with preferential attachment
- **Watts-Strogatz**: Small-world networks with clustering

## Graph Processing

### Filtering Options
- **Zero-Degree Removal**: Exclude isolated nodes from analysis
- **Largest Component**: Focus on main connected component
- **Self-Edge Removal**: Remove self-loops for cleaner analysis

### Graph Types
- **Directed**: Preserves edge direction
- **Undirected**: Treats all edges as bidirectional

## Centrality Measures

### Available Metrics
- **Degree Centrality (Unnormalized)**: Number of direct connections
- **Degree Centrality (Normalized)**: Number of direct connections / Total number of Connections
- **Betweenness Centrality**: Importance as network bridge
- **Closeness Centrality**: Average distance to all nodes
- **Eigenvector Centrality**: Influence based on neighbor importance
- **Katz Centrality**: Weighted sum of path lengths

### Analysis Features
- **Node Removal Impact**: Calculate centrality changes after removing specific nodes
- **Comparative Analysis**: Before/after centrality values
- **Impact Ranking**: Sort nodes by centrality change magnitude

## Visualization

### Graph Display
- **Node Coloring**: Visual representation of impact (red=increase, blue=decrease)
- **Edge Styling**: Thickness based on weights or impact
- **Layout Algorithms**: Automatic positioning for clear visualization
- **Removed Node Marking**: Highlight nodes selected for removal

### Display Options
- **Node Labels**: Show/hide node names
- **Edge Highlighting**: Emphasize affected connections

## Data Views

### Table View
- **Sortable Columns**: Click headers to sort by any metric
- **Impact Calculation**: Shows original, new, and change values
- **Export Ready**: Copy or save tabular results

### Adjacency List
- **Text Representation**: Complete graph structure as text
- **Connection Details**: Shows all node relationships
- **Debugging Aid**: Verify graph loading accuracy

## Export Capabilities

### Result Formats
- **CSV**: Spreadsheet-compatible analysis results
- **SVG**: High-quality graph visualizations
- **CYS**: Cytoscape session with analysis attributes
