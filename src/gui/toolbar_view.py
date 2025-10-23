import tkinter as tk
from tkinter import ttk
from .node_selector_view import NodeSelectorView

class ToolbarView(ttk.Frame):
    def __init__(self, master: tk.Misc, centrality_keys):
        super().__init__(master, padding=(10, 10, 10, 6))

        # Optional callback that can be set by the controller to generate a preview
        self.preview_callback = None

        # Callback for when columns are selected
        self.on_column_selected_callback = None

        # Track collapsed state
        self.is_collapsed = False

        # Create header frame with collapse/expand button and status bar
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        self.header_frame.columnconfigure(1, weight=1)  # Make middle column expand

        # Define toggle behavior as a nested function and attach to self
        def _toggle_collapse():
            self.is_collapsed = not self.is_collapsed
            if self.is_collapsed:
                # hide the content frame
                self.content_frame.pack_forget()
                self.toggle_button.config(text="▶ Configuration")
            else:
                # show the content frame
                self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                self.toggle_button.config(text="▼ Configuration")
        self._toggle_collapse = _toggle_collapse

        # Collapse/Expand button
        self.toggle_button = ttk.Button(self.header_frame, text="▼ Configuration",
                                       command=self._toggle_collapse, width=20)
        self.toggle_button.grid(row=0, column=0, sticky=tk.W)

        # Import and create status bar in the header
        from .status_bar_view import StatusBarView
        self.status_bar = StatusBarView(self.header_frame)
        self.status_bar.grid(row=0, column=2, sticky=tk.E, padx=(10, 0))

        # Create collapsible content frame
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # File selection / Random graph generation section
        file_frame = ttk.Frame(self.content_frame)
        file_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), padx=4, pady=4)
        file_frame.columnconfigure(1, weight=1)  # Make the entry expand

        # Graph source selection (File or Random)
        source_frame = ttk.Frame(file_frame)
        source_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 4))

        ttk.Label(source_frame, text="Graph source:").grid(row=0, column=0, sticky=tk.W, padx=(0, 4))
        self.graph_source_var = tk.StringVar(value="file")
        self.graph_source_combo = ttk.Combobox(source_frame, textvariable=self.graph_source_var,
                                             values=["file", "random"], state="readonly", width=15)
        self.graph_source_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 4))
        self.graph_source_combo.bind('<<ComboboxSelected>>', self._on_graph_source_changed)

        # File selection (shown when source is "file")
        self.file_selection_frame = ttk.Frame(file_frame)
        self.file_selection_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=4)
        self.file_selection_frame.columnconfigure(1, weight=1)

        ttk.Label(self.file_selection_frame, text="Graph file (TSV, CYS, or GEXF)").grid(row=0, column=0, sticky=tk.W, padx=(0, 4))
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(self.file_selection_frame, textvariable=self.file_var, style="Tall.TEntry")
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 4))
        self.browse_button = ttk.Button(self.file_selection_frame, text="Browse", style="Tall.TButton")
        self.browse_button.grid(row=0, column=2, sticky=tk.E)

        # Random graph selection (hidden initially)
        self.random_graph_frame = ttk.Frame(file_frame)
        self.random_graph_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=4)
        self.random_graph_frame.columnconfigure(1, weight=1)
        self.random_graph_frame.columnconfigure(3, weight=1)

        ttk.Label(self.random_graph_frame, text="Graph type:").grid(row=0, column=0, sticky=tk.W, padx=(0, 4))
        self.random_graph_type_var = tk.StringVar(value="erdos_renyi")
        self.random_graph_type_combo = ttk.Combobox(self.random_graph_frame, textvariable=self.random_graph_type_var,
                                                   values=["erdos_renyi", "barabasi_albert", "watts_strogatz"],
                                                   state="readonly", width=18)
        self.random_graph_type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 8))
        self.random_graph_type_combo.bind('<<ComboboxSelected>>', self._on_random_graph_changed)

        ttk.Label(self.random_graph_frame, text="Size (nodes):").grid(row=0, column=2, sticky=tk.W, padx=(0, 4))
        self.random_graph_size_var = tk.StringVar(value="50")
        self.random_graph_size_entry = ttk.Entry(self.random_graph_frame, textvariable=self.random_graph_size_var, width=10)
        self.random_graph_size_entry.grid(row=0, column=3, sticky=(tk.W, tk.E))
        self.random_graph_size_entry.bind('<KeyRelease>', self._on_random_graph_changed)

        self.generate_button = ttk.Button(self.random_graph_frame, text="Generate", style="Tall.TButton")
        self.generate_button.grid(row=0, column=4, sticky=tk.E, padx=(8, 0))

        # Initially hide random graph options
        self.random_graph_frame.grid_remove()

        # Network selection section (for .cys files)
        self.network_label = ttk.Label(self.content_frame, text="Network")
        self.network_label.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        self.network_var = tk.StringVar()
        self.network_combo = ttk.Combobox(self.content_frame, textvariable=self.network_var, width=40, style="Tall.TCombobox", state="readonly")
        self.network_combo.grid(row=1, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=4, pady=4)
        self.network_combo.bind('<<ComboboxSelected>>', self._on_column_selected)
        # Initially hide network selector
        self.network_label.grid_remove()
        self.network_combo.grid_remove()

        # TSV-specific options frame (will be hidden/shown based on file type)
        self.tsv_options_frame = ttk.Frame(self.content_frame)
        self.tsv_options_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), padx=4, pady=4)
        self.tsv_options_frame.columnconfigure(1, weight=1)
        self.tsv_options_frame.columnconfigure(3, weight=1)
        self.tsv_options_frame.columnconfigure(5, weight=1)

        # Column selection section (TSV-specific) - all in one row
        ttk.Label(self.tsv_options_frame, text="Source Node Column").grid(row=0, column=0, sticky=tk.W, padx=(0, 4), pady=4)
        self.edge1_var = tk.StringVar()
        self.edge1_combo = ttk.Combobox(self.tsv_options_frame, textvariable=self.edge1_var, width=12, style="Tall.TCombobox", state="readonly")
        self.edge1_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 8), pady=4)
        self.edge1_combo.bind('<<ComboboxSelected>>', self._on_column_selected)

        ttk.Label(self.tsv_options_frame, text="Destination Node Column").grid(row=0, column=2, sticky=tk.W, padx=(0, 4), pady=4)
        self.edge2_var = tk.StringVar()
        self.edge2_combo = ttk.Combobox(self.tsv_options_frame, textvariable=self.edge2_var, width=12, style="Tall.TCombobox", state="readonly")
        self.edge2_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 8), pady=4)
        self.edge2_combo.bind('<<ComboboxSelected>>', self._on_column_selected)

        ttk.Label(self.tsv_options_frame, text="Weight Column").grid(row=0, column=4, sticky=tk.W, padx=(0, 4), pady=4)
        self.weight_var = tk.StringVar()
        self.weight_combo = ttk.Combobox(self.tsv_options_frame, textvariable=self.weight_var, width=12, style="Tall.TCombobox", state="readonly")
        self.weight_combo.grid(row=0, column=5, sticky=(tk.W, tk.E), padx=(0, 8), pady=4)
        self.weight_combo.bind('<<ComboboxSelected>>', self._on_column_selected)

        # Self-edges removal option and directed/undirected toggle (TSV-specific) - in same row
        self.remove_self_edges_var = tk.BooleanVar(value=True)
        self.directed_graph_var = tk.BooleanVar(value=False)

        self.remove_self_edges_cb = ttk.Checkbutton(
            self.tsv_options_frame,
            text="Remove self-edges",
            variable=self.remove_self_edges_var,
            command=self._on_column_selected
        )
        self.remove_self_edges_cb.grid(row=0, column=6, sticky=tk.W, padx=(8, 4), pady=4)

        self.directed_graph_cb = ttk.Checkbutton(
            self.tsv_options_frame,
            text="Directed graph",
            variable=self.directed_graph_var,
            command=self._on_column_selected
        )
        self.directed_graph_cb.grid(row=0, column=7, sticky=tk.W, padx=(4, 0), pady=4)

        # Initially hide TSV-specific options
        self.tsv_options_frame.grid_remove()

        # Graph processing options (visible for all graph types) - moved to row 3
        ttk.Label(self.content_frame, text="Graph processing").grid(row=3, column=0, sticky=tk.NW, padx=4, pady=4)
        graph_processing_frame = ttk.Frame(self.content_frame)
        graph_processing_frame.grid(row=3, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=4, pady=4)

        # Remove zero degree nodes option
        self.remove_zero_degree_var = tk.BooleanVar(value=False)
        self.remove_zero_degree_cb = ttk.Checkbutton(
            graph_processing_frame,
            text="Remove zero degree nodes",
            variable=self.remove_zero_degree_var,
            command=self._on_graph_processing_changed
        )
        self.remove_zero_degree_cb.grid(row=0, column=0, sticky=tk.W, padx=(0, 20), pady=2)

        # Use only largest component option
        self.use_largest_component_var = tk.BooleanVar(value=False)
        self.use_largest_component_cb = ttk.Checkbutton(
            graph_processing_frame,
            text="Use only the largest component",
            variable=self.use_largest_component_var,
            command=self._on_graph_processing_changed
        )
        self.use_largest_component_cb.grid(row=0, column=1, sticky=tk.W, padx=0, pady=2)
        # Node selector with multi-select - moved to row 4
        ttk.Label(self.content_frame, text="Nodes to remove").grid(row=4, column=0, sticky=tk.NW, padx=4, pady=4)
        self.node_selector = NodeSelectorView(self.content_frame)
        self.node_selector.grid(row=4, column=1, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=4, pady=4)

        # Centrality measures - use full horizontal space - moved to row 5
        ttk.Label(self.content_frame, text="Centrality measures").grid(row=5, column=0, sticky=tk.NW, padx=4, pady=4)
        self.centrality_vars = {}
        centralities_frame = ttk.Frame(self.content_frame)
        centralities_frame.grid(row=5, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=4, pady=4)
        centralities_frame.columnconfigure(0, weight=1)
        centralities_frame.columnconfigure(1, weight=1)
        centralities_frame.columnconfigure(2, weight=1)

        # Create user-friendly display names for centrality measures
        centrality_display_names = {
            "degree": "Degree (Normalized)",
            "unnormalized_degree": "Degree (Unnormalized)",
            "betweenness": "Betweenness",
            "closeness": "Closeness",
            "eigenvector": "Eigenvector",
            "katz": "Katz"
        }

        for i, key in enumerate(centrality_keys):
            var = tk.BooleanVar(value=(key in ("degree", "betweenness", "closeness")))
            display_name = centrality_display_names.get(key, key.title())
            cb = ttk.Checkbutton(centralities_frame, text=display_name, variable=var)
            # Use multiple rows if we have many centrality options
            row = i // 3
            col = i % 3
            cb.grid(row=row, column=col, padx=4, pady=2, sticky=tk.W)
            self.centrality_vars[key] = var

        # Plot options - moved to row 6
        ttk.Label(self.content_frame, text="Plot options").grid(row=6, column=0, sticky=tk.NW, padx=4, pady=4)
        plot_options_frame = ttk.Frame(self.content_frame)
        plot_options_frame.grid(row=6, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=4, pady=4)

        # Layout type selection
        layout_frame = ttk.Frame(plot_options_frame)
        layout_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=4, pady=2)

        ttk.Label(layout_frame, text="Layout:").grid(row=0, column=0, padx=(0, 4), sticky=tk.W)
        self.layout_type_var = tk.StringVar(value="Spring")
        self.layout_type_combo = ttk.Combobox(layout_frame, textvariable=self.layout_type_var,
                                            values=["Spring", "Circular"],
                                            state="readonly", width=12)
        self.layout_type_combo.grid(row=0, column=1, padx=4, sticky=tk.W)

        self.show_node_names_var = tk.BooleanVar(value=True)
        self.show_node_names_cb = ttk.Checkbutton(plot_options_frame, text="Show node names", variable=self.show_node_names_var)
        self.show_node_names_cb.grid(row=1, column=0, padx=4, pady=2, sticky=tk.W)

        self.edge_thickness_by_weight_var = tk.BooleanVar(value=True)
        self.edge_thickness_by_weight_cb = ttk.Checkbutton(plot_options_frame, text="Edge thickness by weight", variable=self.edge_thickness_by_weight_var)
        self.edge_thickness_by_weight_cb.grid(row=1, column=1, padx=4, pady=2, sticky=tk.W)

        self.mark_removed_edges_var = tk.BooleanVar(value=True)
        self.mark_removed_edges_cb = ttk.Checkbutton(plot_options_frame, text="Mark removed edges", variable=self.mark_removed_edges_var)
        self.mark_removed_edges_cb.grid(row=1, column=2, padx=4, pady=2, sticky=tk.W)

        # Action buttons - moved to row 7
        actions_frame = ttk.Frame(self.content_frame)
        actions_frame.grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E), padx=0, pady=(6, 0))
        self.run_button = ttk.Button(actions_frame, text="Run Analysis")
        self.run_button.pack(side=tk.LEFT, padx=(0, 6))
        self.refresh_plot_button = ttk.Button(actions_frame, text="Refresh Plot")
        self.refresh_plot_button.pack(side=tk.LEFT, padx=(0, 6))
        self.save_button = ttk.Button(actions_frame, text="Save SVG As...")
        self.save_button.pack(side=tk.LEFT, padx=(0, 6))
        self.clear_button = ttk.Button(actions_frame, text="Clear")
        self.clear_button.pack(side=tk.LEFT)

        # Configure grid weights for proper resizing
        self.content_frame.columnconfigure(1, weight=1)
        self.content_frame.columnconfigure(2, weight=1)
        self.content_frame.columnconfigure(3, weight=1)
        self.content_frame.rowconfigure(4, weight=1)
        self.content_frame.rowconfigure(4, weight=1)

    def _toggle_collapse(self):
        """Toggle the collapsed state of the configuration section"""
        if self.is_collapsed:
            self._expand()
        else:
            self._collapse()

    def _collapse(self):
        """Collapse the configuration section"""
        self.content_frame.pack_forget()
        self.toggle_button.configure(text="▶ Configuration")
        self.is_collapsed = True

    def _expand(self):
        """Expand the configuration section"""
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.toggle_button.configure(text="▼ Configuration")
        self.is_collapsed = False

    def update_column_suggestions(self, columns):
        """Update the column suggestions in the comboboxes"""
        self.edge1_combo['values'] = columns
        self.edge2_combo['values'] = columns
        self.weight_combo['values'] = columns

    def disable_column_selection(self):
        """Disable column selection widgets"""
        self.edge1_combo.configure(state="disabled")
        self.edge2_combo.configure(state="disabled")
        self.weight_combo.configure(state="disabled")
        self.remove_self_edges_cb.configure(state="disabled")
        self.directed_graph_cb.configure(state="disabled")

    def enable_column_selection(self):
        """Enable column selection widgets"""
        self.edge1_combo.configure(state="readonly")
        self.edge2_combo.configure(state="readonly")
        self.weight_combo.configure(state="readonly")
        self.remove_self_edges_cb.configure(state="normal")
        self.directed_graph_cb.configure(state="normal")

    def _on_column_selected(self, _event=None):
        """Handle column selection events"""
        if self.on_column_selected_callback:
            self.on_column_selected_callback()

    def _on_graph_processing_changed(self, _event=None):
        """Handle graph processing option changes"""
        if self.on_column_selected_callback:
            self.on_column_selected_callback()

    def set_column_selected_callback(self, callback):
        """Set the callback for column selection events"""
        self.on_column_selected_callback = callback

    def update_node_list(self, nodes):
        """Update the node list in the node selector"""
        self.node_selector.set_nodes(nodes)

    def get_selected_nodes(self):
        """Get the selected nodes from the node selector"""
        return self.node_selector.get_selected_nodes()

    def clear_node_selector(self):
        """Clear the node selector"""
        self.node_selector.clear()

    def collapse(self):
        """Programmatically collapse the configuration section"""
        if not self.is_collapsed:
            self._collapse()

    def expand(self):
        """Programmatically expand the configuration section"""
        if self.is_collapsed:
            self._expand()

    def update_network_list(self, networks):
        """Update the network list in the network selector"""
        self.network_combo['values'] = networks
        if networks:
            self.network_combo.set(networks[0])
            self.show_network_selector()  # Show the network selector when networks are available
        else:
            self.hide_network_selector()  # Hide if no networks available

    def show_network_selector(self):
        """Show the network selector for .cys files"""
        self.network_label.grid()
        self.network_combo.grid()

    def hide_network_selector(self):
        """Hide the network selector"""
        self.network_label.grid_remove()
        self.network_combo.grid_remove()

    def show_tsv_options(self):
        """Show TSV-specific options"""
        self.tsv_options_frame.grid()

    def hide_tsv_options(self):
        """Hide TSV-specific options"""
        self.tsv_options_frame.grid_remove()

    def _on_graph_source_changed(self, _event=None):
        """Handle graph source selection change"""
        source = self.graph_source_var.get()
        if source == "file":
            self.file_selection_frame.grid()
            self.random_graph_frame.grid_remove()
        else:  # random
            self.file_selection_frame.grid_remove()
            self.random_graph_frame.grid()
            # Hide file-specific options when switching to random
            self.hide_network_selector()
            self.hide_tsv_options()

        # Trigger callback if set
        if getattr(self, "on_column_selected_callback", None):
            self.on_column_selected_callback()

    def _on_random_graph_changed(self, _event=None):
        """Handle random graph parameter changes"""
        # Clear any existing layout cache when parameters change
        if hasattr(self, 'master') and hasattr(self.master, '_controller'):
            controller = getattr(self.master, '_controller', None)
            if controller is not None and hasattr(controller, 'layout_cache'):
                try:
                    controller.layout_cache.clear()
                    # Trigger callback if set
                    if getattr(self, "on_column_selected_callback", None):
                        self.on_column_selected_callback()
                except Exception:
                    # If layout_cache does not support clear(), try to reset it
                    try:
                        controller.layout_cache = {}
                    except Exception:
                        pass

        if getattr(self, "on_column_selected_callback", None):
            self.on_column_selected_callback()

    def is_random_graph_mode(self):
        """Check if currently in random graph mode"""
        return self.graph_source_var.get() == "random"

    def get_random_graph_params(self):
        """Get random graph generation parameters"""
        try:
            size = int(self.random_graph_size_var.get())
            if size <= 0:
                raise ValueError("Size must be positive")
        except Exception:
            size = 50  # default
            try:
                self.random_graph_size_var.set("50")
            except Exception:
                pass

        return {
            'graph_type': self.random_graph_type_var.get(),
            'size': size
        }

    def get_selected_network(self):
        """Get the selected network name for .cys files"""
        return self.network_var.get() if hasattr(self, 'network_var') else None


