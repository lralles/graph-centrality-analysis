import tkinter as tk
from tkinter import ttk

class ToolbarView(ttk.Frame):
    def __init__(self, master: tk.Misc, centrality_keys):
        super().__init__(master, padding=(10, 10, 10, 6))

        ttk.Label(self, text="Graph TSV file").grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        self.file_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.file_var, width=60, style="Tall.TEntry").grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        self.browse_button = ttk.Button(self, text="Browse", style="Tall.TButton")
        self.browse_button.grid(row=0, column=2, padx=4, pady=4, sticky=tk.W)

        ttk.Label(self, text="Edge 1 column").grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        self.edge1_var = tk.StringVar(value="edge1")
        ttk.Entry(self, textvariable=self.edge1_var, width=20, style="Tall.TEntry").grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)

        ttk.Label(self, text="Edge 2 column").grid(row=1, column=2, sticky=tk.W, padx=4, pady=4)
        self.edge2_var = tk.StringVar(value="edge2")
        ttk.Entry(self, textvariable=self.edge2_var, width=20, style="Tall.TEntry").grid(row=1, column=3, sticky=tk.W, padx=4, pady=4)

        ttk.Label(self, text="Weight column").grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        self.weight_var = tk.StringVar(value="weight")
        ttk.Entry(self, textvariable=self.weight_var, width=20, style="Tall.TEntry").grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)

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

        actions_frame = ttk.Frame(self)
        actions_frame.grid(row=5, column=0, columnspan=4, sticky=tk.W, padx=0, pady=(6, 0))
        self.run_button = ttk.Button(actions_frame, text="Run Analysis")
        self.run_button.pack(side=tk.LEFT, padx=(0, 6))
        self.save_button = ttk.Button(actions_frame, text="Save SVG As...")
        self.save_button.pack(side=tk.LEFT, padx=(0, 6))
        self.clear_button = ttk.Button(actions_frame, text="Clear")
        self.clear_button.pack(side=tk.LEFT)


