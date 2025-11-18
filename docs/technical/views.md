# Views Documentation

The view layer implements the user interface using Tkinter components.

## MainWindow (`main_window.py`)

**Purpose**: Main application window and GUI coordinator

**Dependencies**: 
- `tkinter`, `ttk`
- All other view components
- Controller and model instances

**Key Methods**:
- `__init__()`: Initializes GUI and binds controller
- `_build_widgets()`: Creates and arranges UI components
- `_initialize_with_random_graph()`: Sets up default random graph
- `show_*_dialog()`: Various dialog windows for user input

## ToolbarView (`toolbar_view.py`)

**Purpose**: Top toolbar with file operations and analysis controls

**Dependencies**: 
- `tkinter`, `ttk`
- File dialog components

**Key Methods**:
- `create_toolbar()`: Builds toolbar layout
- `get_selected_centrality()`: Returns chosen centrality measure
- `is_random_graph_mode()`: Checks if using random graph
- Various getter methods for user selections

## PlotView (`plot_view.py`)

**Purpose**: Graph visualization area using matplotlib

**Dependencies**: 
- `matplotlib`, `tkinter`
- PlotRenderer for actual drawing

**Key Methods**:
- `create_plot_area()`: Sets up matplotlib canvas
- `clear_plot()`: Removes current visualization
- `update_plot()`: Refreshes display

## PlotRenderer (`plot_renderer.py`)

**Purpose**: Handles graph drawing and visualization logic

**Dependencies**: 
- `matplotlib`, `networkx`
- LayoutCache for consistent positioning

**Key Methods**:
- `render()`: Main rendering method
- `_draw_nodes()`: Draws graph nodes with styling
- `_draw_edges()`: Draws graph edges with weights/highlighting
- `_apply_node_colors()`: Colors nodes based on impact/removal

## TableView (`table_view.py`)

**Purpose**: Displays analysis results in tabular format

**Dependencies**: 
- `tkinter.ttk.Treeview`
- `pandas` for data handling

**Key Methods**:
- `create_table()`: Sets up table widget
- `update_table()`: Populates table with analysis results
- `clear_table()`: Removes all table data

## Additional Views

- **NodeSelectorView**: Dialog for selecting nodes to remove
- **AdjacencyListView**: Shows graph structure as adjacency list
- **StatusBarView**: Displays application status and progress