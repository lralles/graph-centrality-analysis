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

        # Create header frame with collapse/expand button
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

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
        self.toggle_button.pack(side=tk.LEFT)

        # Create collapsible content frame
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # File selection section
        ttk.Label(self.content_frame, text="Graph file (TSV or CYS)").grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        self.file_var = tk.StringVar()
        ttk.Entry(self.content_frame, textvariable=self.file_var, width=60, style="Tall.TEntry").grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        self.browse_button = ttk.Button(self.content_frame, text="Browse", style="Tall.TButton")
        self.browse_button.grid(row=0, column=2, padx=4, pady=4, sticky=tk.W)

        # Column selection section
        ttk.Label(self.content_frame, text="Source Node Column").grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        self.edge1_var = tk.StringVar()
        self.edge1_combo = ttk.Combobox(self.content_frame, textvariable=self.edge1_var, width=18, style="Tall.TCombobox", state="readonly")
        self.edge1_combo.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
        self.edge1_combo.bind('<<ComboboxSelected>>', self._on_column_selected)

        ttk.Label(self.content_frame, text="Destination Node Column").grid(row=1, column=2, sticky=tk.W, padx=4, pady=4)
        self.edge2_var = tk.StringVar()
        self.edge2_combo = ttk.Combobox(self.content_frame, textvariable=self.edge2_var, width=18, style="Tall.TCombobox", state="readonly")
        self.edge2_combo.grid(row=1, column=3, sticky=tk.W, padx=4, pady=4)
        self.edge2_combo.bind('<<ComboboxSelected>>', self._on_column_selected)

        ttk.Label(self.content_frame, text="Weight Column").grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        self.weight_var = tk.StringVar()
        self.weight_combo = ttk.Combobox(self.content_frame, textvariable=self.weight_var, width=18, style="Tall.TCombobox", state="readonly")
        self.weight_combo.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)
        self.weight_combo.bind('<<ComboboxSelected>>', self._on_column_selected)

        # Self-edges removal option
        self.remove_self_edges_var = tk.BooleanVar(value=True)
        self.remove_self_edges_cb = ttk.Checkbutton(self.content_frame, text="Remove self-edges (loops)", variable=self.remove_self_edges_var, command=self._on_column_selected)
        self.remove_self_edges_cb.grid(row=2, column=2, columnspan=2, sticky=tk.W, padx=4, pady=4)

        # Node selector with multi-select
        ttk.Label(self.content_frame, text="Nodes to remove").grid(row=3, column=0, sticky=tk.NW, padx=4, pady=4)
        self.node_selector = NodeSelectorView(self.content_frame)
        self.node_selector.grid(row=3, column=1, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=4, pady=4)

        ttk.Label(self.content_frame, text="Centrality measures").grid(row=4, column=0, sticky=tk.NW, padx=4, pady=4)
        self.centrality_vars = {}
        centralities_frame = ttk.Frame(self.content_frame)
        centralities_frame.grid(row=4, column=1, columnspan=3, sticky=tk.W, padx=4, pady=4)

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

        # Plot options
        ttk.Label(self.content_frame, text="Plot options").grid(row=5, column=0, sticky=tk.NW, padx=4, pady=4)
        plot_options_frame = ttk.Frame(self.content_frame)
        plot_options_frame.grid(row=5, column=1, columnspan=3, sticky=tk.W, padx=4, pady=4)

        self.show_node_names_var = tk.BooleanVar(value=True)
        self.show_node_names_cb = ttk.Checkbutton(plot_options_frame, text="Show node names", variable=self.show_node_names_var)
        self.show_node_names_cb.grid(row=0, column=0, padx=4, pady=2, sticky=tk.W)

        self.edge_thickness_by_weight_var = tk.BooleanVar(value=True)
        self.edge_thickness_by_weight_cb = ttk.Checkbutton(plot_options_frame, text="Edge thickness by weight", variable=self.edge_thickness_by_weight_var)
        self.edge_thickness_by_weight_cb.grid(row=0, column=1, padx=4, pady=2, sticky=tk.W)

        self.mark_removed_edges_var = tk.BooleanVar(value=True)
        self.mark_removed_edges_cb = ttk.Checkbutton(plot_options_frame, text="Mark removed edges", variable=self.mark_removed_edges_var)
        self.mark_removed_edges_cb.grid(row=0, column=2, padx=4, pady=2, sticky=tk.W)

        # Action buttons
        actions_frame = ttk.Frame(self.content_frame)
        actions_frame.grid(row=6, column=0, columnspan=4, sticky=tk.W, padx=0, pady=(6, 0))
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
        self.content_frame.rowconfigure(3, weight=1)

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

    def enable_column_selection(self):
        """Enable column selection widgets"""
        self.edge1_combo.configure(state="readonly")
        self.edge2_combo.configure(state="readonly")
        self.weight_combo.configure(state="readonly")
        self.remove_self_edges_cb.configure(state="normal")

    def _on_column_selected(self, _event=None):
        """Handle column selection events"""
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


