import tkinter as tk
from tkinter import ttk

class NodeSelectorView(ttk.Frame):
    """A widget for selecting multiple nodes from a list with search functionality"""

    def __init__(self, master: tk.Misc):
        super().__init__(master)

        # Search frame
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self._on_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Listbox with scrollbar
        listbox_frame = ttk.Frame(self)
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(
            listbox_frame,
            selectmode=tk.EXTENDED,
            yscrollcommand=scrollbar.set,
            height=8,
            exportselection=False
        )
        scrollbar.config(command=self.listbox.yview)

        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Store all nodes for filtering
        self._all_nodes = []

    def set_nodes(self, nodes: list[str]):
        """Set the available nodes in the listbox"""
        self._all_nodes = sorted(nodes)
        self._update_listbox()

    def get_selected_nodes(self) -> list[str]:
        """Get the currently selected nodes"""
        selected_indices = self.listbox.curselection()
        return [self.listbox.get(i) for i in selected_indices]

    def set_selected_nodes(self, nodes: list[str]):
        """Set which nodes should be selected"""
        self.listbox.selection_clear(0, tk.END)
        for i in range(self.listbox.size()):
            if self.listbox.get(i) in nodes:
                self.listbox.selection_set(i)

    def _update_listbox(self):
        """Update the listbox based on current filter"""
        # Store current selection
        current_selection = self.get_selected_nodes()

        # Clear and repopulate
        self.listbox.delete(0, tk.END)

        search_term = self.search_var.get().lower()
        filtered_nodes = [n for n in self._all_nodes if search_term in n.lower()]

        for node in filtered_nodes:
            self.listbox.insert(tk.END, node)

        # Restore selection
        self.set_selected_nodes(current_selection)

    def _on_search(self, *_args):
        """Called when search text changes"""
        self._update_listbox()