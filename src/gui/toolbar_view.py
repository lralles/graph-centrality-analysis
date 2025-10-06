import tkinter as tk
from tkinter import ttk

class ToolbarView(ttk.Frame):
    def __init__(self, master: tk.Misc, centrality_keys):
        super().__init__(master, padding=(10, 10, 10, 6))

        # Optional callback that can be set by the controller to generate a preview
        self.preview_callback = None

        # Callback for when columns are selected
        self.on_column_selected_callback = None

        ttk.Label(self, text="Graph TSV file").grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        self.file_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.file_var, width=60, style="Tall.TEntry").grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        self.browse_button = ttk.Button(self, text="Browse", style="Tall.TButton")
        self.browse_button.grid(row=0, column=2, padx=4, pady=4, sticky=tk.W)

        ttk.Label(self, text="Edge 1 column").grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        self.edge1_var = tk.StringVar()
        self.edge1_combo = ttk.Combobox(self, textvariable=self.edge1_var, width=18, style="Tall.TCombobox", state="readonly")
        self.edge1_combo.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
        self.edge1_combo.bind('<<ComboboxSelected>>', self._on_column_selected)

        ttk.Label(self, text="Edge 2 column").grid(row=1, column=2, sticky=tk.W, padx=4, pady=4)
        self.edge2_var = tk.StringVar()
        self.edge2_combo = ttk.Combobox(self, textvariable=self.edge2_var, width=18, style="Tall.TCombobox", state="readonly")
        self.edge2_combo.grid(row=1, column=3, sticky=tk.W, padx=4, pady=4)
        self.edge2_combo.bind('<<ComboboxSelected>>', self._on_column_selected)

        ttk.Label(self, text="Weight column").grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        self.weight_var = tk.StringVar()
        self.weight_combo = ttk.Combobox(self, textvariable=self.weight_var, width=18, style="Tall.TCombobox", state="readonly")
        self.weight_combo.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)
        self.weight_combo.bind('<<ComboboxSelected>>', self._on_column_selected)

        # Self-edges removal option
        self.remove_self_edges_var = tk.BooleanVar(value=True)
        self.remove_self_edges_cb = ttk.Checkbutton(self, text="Remove self-edges (loops)", variable=self.remove_self_edges_var, command=self._on_column_selected)
        self.remove_self_edges_cb.grid(row=2, column=2, columnspan=2, sticky=tk.W, padx=4, pady=4)

        ttk.Label(self, text="Removed nodes (space-separated)").grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
        self.removed_nodes_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.removed_nodes_var, width=60, style="Tall.TEntry").grid(row=3, column=1, columnspan=3, sticky=tk.W, padx=4, pady=4)

        ttk.Label(self, text="Centrality measures").grid(row=4, column=0, sticky=tk.NW, padx=4, pady=4)
        self.centrality_vars = {}
        centralities_frame = ttk.Frame(self)
        centralities_frame.grid(row=4, column=1, columnspan=3, sticky=tk.W, padx=4, pady=4)
        for i, key in enumerate(centrality_keys):
            var = tk.BooleanVar(value=(key in ("degree", "betweenness", "closeness")))
            cb = ttk.Checkbutton(centralities_frame, text=key, variable=var)
            cb.grid(row=0, column=i, padx=4, pady=2, sticky=tk.W)
            self.centrality_vars[key] = var

        # Plot options
        ttk.Label(self, text="Plot options").grid(row=5, column=0, sticky=tk.NW, padx=4, pady=4)
        plot_options_frame = ttk.Frame(self)
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

        actions_frame = ttk.Frame(self)
        actions_frame.grid(row=6, column=0, columnspan=4, sticky=tk.W, padx=0, pady=(6, 0))
        self.run_button = ttk.Button(actions_frame, text="Run Analysis")
        self.run_button.pack(side=tk.LEFT, padx=(0, 6))
        self.refresh_plot_button = ttk.Button(actions_frame, text="Refresh Plot")
        self.refresh_plot_button.pack(side=tk.LEFT, padx=(0, 6))
        self.save_button = ttk.Button(actions_frame, text="Save SVG As...")
        self.save_button.pack(side=tk.LEFT, padx=(0, 6))
        self.clear_button = ttk.Button(actions_frame, text="Clear")
        self.clear_button.pack(side=tk.LEFT)

    def update_column_suggestions(self, columns):
        """Update the dropdown options for column comboboxes"""
        self.edge1_combo['values'] = columns
        self.edge2_combo['values'] = columns
        self.weight_combo['values'] = columns

    def _on_column_selected(self, _event=None):
        """Called when a column is selected in any combobox"""
        if self.on_column_selected_callback:
            self.on_column_selected_callback()

    def set_column_selected_callback(self, callback):
        """Set the callback function for when columns are selected"""
        self.on_column_selected_callback = callback


