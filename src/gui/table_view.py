import tkinter as tk
from tkinter import ttk
import pandas as pd

class TableView(ttk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        columns = ("node", "new", "diff")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor=tk.W, stretch=True)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        try:
            self.tree.tag_configure('oddrow', background='#2a2d2e')
        except Exception:
            pass

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def populate(self, df: pd.DataFrame):
        self.clear()
        for idx, (node, row) in enumerate(df.iterrows()):
            import numpy as _np
            new_val = row.get("new", _np.nan)
            diff_val = row.get("diff", _np.nan)
            tag = 'oddrow' if idx % 2 else ''
            self.tree.insert("", tk.END, values=(str(node), f"{new_val:.6f}", f"{diff_val:.6f}"), tags=(tag,))


