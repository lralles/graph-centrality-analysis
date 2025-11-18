# File Formats

The application supports multiple graph file formats for maximum compatibility.

## TSV (Tab-Separated Values)

**Format**: Plain text with tab-separated columns
**Extension**: `.tsv`

### Structure
```
source_node    target_node    weight
A              B              1.5
B              C              2.0
C              A              0.8
```

### Configuration
When loading TSV files, specify:
- **Source Column**: Column containing source node IDs
- **Target Column**: Column containing target node IDs  
- **Weight Column**: Column containing edge weights (optional)

### Requirements
- First row can be headers (automatically detected)
- Node IDs can be text or numeric
- Weight values must be numeric

## CYS (Cytoscape Session)

**Format**: Cytoscape session file (ZIP archive)
**Extension**: `.cys`

### Features
- Contains complete network data with attributes
- May include multiple networks in one file

### Loading Process
1. Application extracts and lists available networks
2. User selects which network to analyze
3. Node and edge attributes are preserved

## GEXF (Graph Exchange XML Format)

**Format**: XML-based graph format
**Extension**: `.gexf`

### Features
- Standardized graph exchange format
