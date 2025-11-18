# Workflow Guide

This guide walks through the complete analysis workflow from data loading to result visualization.

## Step 1: Graph Selection

### Option A: Load from File
1. Click "Select File" in the toolbar
2. Choose your graph file (TSV, CYS, or GEXF format)
3. For TSV files: Configure column mappings in the dialog
4. For CYS files: Select which network to analyze

### Option B: Generate Random Graph
1. Click "Random Graph" in the toolbar
2. Choose graph type (Erdős-Rényi, Barabási-Albert, Watts-Strogatz, Complete)
3. Set parameters (number of nodes, edges, probability)
4. Click "Generate"

## Step 2: Graph Configuration

### Processing Options
- **Remove Zero-Degree Nodes**: Excludes isolated nodes
- **Use Largest Component**: Analyzes only the main connected component
- **Remove Self-Edges**: Eliminates self-loops

### Preview Generation
1. Review the adjacency list to understand graph structure
2. Check node count and edge statistics

## Step 3: Analysis Setup

### Node Selection
1. Click "Select Nodes to Remove"
2. Choose nodes from the list (supports multiple selection)

### Centrality Measure
Select from available measures:
- **Degree**: Number of connections
- **Betweenness**: Shortest path intermediary importance
- **Closeness**: Average distance to all other nodes
- **Eigenvector**: Influence based on neighbor importance
- **Katz**: Weighted sum of path lengths

## Step 4: Run Analysis

1. Click "Run Analysis" to start computation
2. Monitor progress in the status bar
3. Analysis runs in background to keep UI responsive

## Step 5: Review Results

### Table View
- Shows centrality changes for each remaining node
- Columns: Node ID, New Centrality, Impact (Δ), New Combined Centrality, Combined Impact (Δ)
- Sortable by any column

### Graph Visualization
- **Node Colors**: Represent impact magnitude (red=positive, blue=negative)
- **Node Labels**: Toggle node names on/off
- **Edge Highlighting**: Highlights removed edges
- **Removed Nodes**: Highlighted in different color

### Visualization Options
- Show/hide node names
- Adjust edge thickness by weight
- Highlight edges affected by node removal

## Step 6: Export Results

### Save Options
- **CSV**: Analysis results as spreadsheet
- **SVG**: Graph visualization as image
- **CYS**: Cytoscape session with results

