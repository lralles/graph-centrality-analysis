# Controllers Documentation

The controller layer manages business logic and coordinates between views and models.

## GraphAnalysisController (`graph_analysis_controller.py`)

**Purpose**: Main controller handling all user interactions and business logic

**Dependencies**: 
- MainWindow (app)
- GraphLoader (loader)
- CentralityAnalysisService (analysis)
- LayoutCache (layout_cache)
- PlotRenderer (renderer)

**Key Methods**:

### Graph Management
- `generate_preview()`: Creates graph preview visualization
- `set_random_graph()`: Sets random graph for analysis
- `load_graph_from_file()`: Handles file-based graph loading

### Analysis Operations
- `run_analysis()`: Executes centrality analysis with node removal
- `_perform_analysis()`: Core analysis logic (runs in separate thread)
- `_on_analysis_complete()`: Handles analysis completion

### File Operations
- `save_results()`: Exports analysis results to various formats
- `export_graph()`: Saves current graph state

### UI Event Handlers
- `on_file_select()`: Processes file selection events
- `on_centrality_change()`: Handles centrality measure changes
- `on_node_selection()`: Manages node selection for removal

### Data Flow
1. User interaction triggers view event
2. View calls appropriate controller method
3. Controller validates input and calls model methods
4. Controller processes model results
5. Controller updates views with new data

### Error Handling
- Validates file formats and graph structure
- Handles missing data and invalid selections
- Provides user feedback for errors and warnings