# Graph Centrality Analysis

A comprehensive tool for analyzing how node removal affects centrality measures in network graphs. Supports multiple file formats and provides interactive visualization of network structure and analysis results.

## Features

- **Multiple File Formats**: TSV, CYS (Cytoscape), and GEXF support
- **Random Graph Generation**: Built-in generators for testing and exploration
- **Centrality Measures**: Degree (Normalized and Unnormalized), Betweenness, Closeness, Eigenvector and Katz
- **Interactive Visualization**: Graph plots with impact highlighting and customizable display options
- **Export Capabilities**: Save results in CSV, SVG, CYS

## Documentation

### 📖 User Guide
- **[Getting Started](docs/wiki/getting-started.md)** - Installation and first steps
- **[Workflow Guide](docs/wiki/workflow.md)** - Complete analysis process
- **[File Formats](docs/wiki/file-formats.md)** - Supported input formats
- **[Features](docs/wiki/features.md)** - Available analysis options
- **[Examples](docs/wiki/examples.md)** - Sample analyses and use cases

### 🔧 Technical Documentation
- **[Architecture Overview](docs/technical/mvc-architecture.md)** - MVC pattern implementation
- **[Models](docs/technical/models.md)** - Data layer and analysis services
- **[Views](docs/technical/views.md)** - GUI components and visualization
- **[Controllers](docs/technical/controllers.md)** - Business logic and event handling
- **[Dependencies](docs/technical/dependencies.md)** - Required libraries
- **[Compilation](docs/technical/compilation.md)** - Building executables and automated builds

## Workflow Overview

1. **Load Graph**: Select file (TSV/CYS/GEXF) or generate random graph
2. **Configure**: Set column mappings or network selection
3. **Preview**: View graph structure and adjacency list
4. **Select**: Choose nodes to remove and centrality measure
5. **Analyze**: Run analysis to calculate impact on remaining nodes
6. **Visualize**: Explore results in table and graph views
7. **Export**: Save results and visualizations
