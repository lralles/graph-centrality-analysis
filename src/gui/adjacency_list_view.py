import tkinter as tk
from tkinter import ttk
import networkx as nx


class AdjacencyListView(ttk.Frame):
    """
    A view component that displays the adjacency list of a graph in table format.
    Shows each node and its adjacent nodes.
    """
    
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        
        # Create a label for the table
        label = ttk.Label(self, text="Graph Adjacency List", font=("Segoe UI", 11, "bold"))
        label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5, 2))
        
        # Create frame for the treeview and scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Initialize treeview with two columns
        self.columns = ("adjacent_nodes",)
        self.tree = ttk.Treeview(
            tree_frame, 
            columns=self.columns, 
            show="tree headings", 
            selectmode="extended"
        )
        
        # Configure the tree column (node names)
        self.tree.heading("#0", text="Node", command=lambda: self._sort_column("#0", False))
        self.tree.column("#0", width=150, anchor=tk.W, stretch=True)
        
        # Configure the adjacent nodes column
        self.tree.heading("adjacent_nodes", text="Adjacent Nodes", 
                         command=lambda: self._sort_column("adjacent_nodes", False))
        self.tree.column("adjacent_nodes", width=400, anchor=tk.W, stretch=True)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=v_scrollbar.set, xscroll=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Configure alternating row colors (zebra striping)
        try:
            self.tree.tag_configure('evenrow', background='#f0f0f0')  # Light grey
            self.tree.tag_configure('oddrow', background='#e0e0e0')   # Medium grey
        except Exception:
            pass
        
        # Track sort direction for each column
        self.sort_reverse = {}
    
    def _sort_column(self, col, reverse):
        """Sort treeview contents by the specified column"""
        # Get all items and their values
        items = []
        for child in self.tree.get_children(''):
            if col == "#0":
                value = self.tree.item(child, "text")
            else:
                value = self.tree.set(child, col)
            items.append((value, child))
        
        # Sort items (string sort for node names and adjacency lists)
        items.sort(key=lambda x: str(x[0]).lower(), reverse=reverse)
        
        # Rearrange items in sorted positions
        for index, (val, child) in enumerate(items):
            self.tree.move(child, '', index)
            # Update row colors
            tag = 'oddrow' if index % 2 else 'evenrow'
            self.tree.item(child, tags=(tag,))
        
        # Update sort direction for next click
        self.sort_reverse[col] = not reverse
        
        # Update column heading to show sort direction
        heading_text = self.tree.heading(col)["text"]
        if heading_text:
            base_text = heading_text.rstrip(" ↑↓")
            arrow = " ↓" if reverse else " ↑"
            self.tree.heading(col, text=base_text + arrow)
    
    def clear(self):
        """Clear all items from the treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def populate(self, graph: nx.Graph):
        """
        Populate the treeview with adjacency list data from a NetworkX graph.
        
        Args:
            graph: A NetworkX Graph object
        """
        self.clear()
        
        if graph is None or graph.number_of_nodes() == 0:
            return
        
        # Get sorted list of nodes
        nodes = sorted(graph.nodes())
        
        # Populate data
        for idx, node in enumerate(nodes):
            # Get adjacent nodes (neighbors)
            neighbors = sorted(graph.neighbors(node))
            
            # Format the adjacent nodes as a comma-separated string
            if neighbors:
                adjacent_str = ", ".join(str(n) for n in neighbors)
            else:
                adjacent_str = "(no adjacent nodes)"
            
            # Insert row with alternating colors
            tag = 'oddrow' if idx % 2 else 'evenrow'
            self.tree.insert("", tk.END, text=str(node), values=(adjacent_str,), tags=(tag,))