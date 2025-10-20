import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import csv

class TableView(ttk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        
        # Create a frame for the export button
        button_frame = ttk.Frame(self)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        self.export_button = ttk.Button(button_frame, text="Export as CSV", command=self._export_csv)
        self.export_button.pack(side=tk.RIGHT)
        
        # Create frame for the treeview and scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Initialize with default columns (will be updated dynamically)
        self.columns = ("node",)
        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show="tree headings", selectmode="extended")
        
        # Configure the tree column (node names)
        self.tree.heading("#0", text="Node", command=lambda: self._sort_column("#0", False))
        self.tree.column("#0", width=140, anchor=tk.W, stretch=True)
        
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
        
        # Store current data for export
        self.current_data = None
        self.sort_reverse = {}  # Track sort direction for each column

    def _sort_column(self, col, reverse):
        """Sort treeview contents by the specified column"""
        if self.current_data is None:
            return

        # Get all items and their values
        items = [(self.tree.set(child, col) if col != "#0" else self.tree.item(child, "text"), child)
                for child in self.tree.get_children('')]

        # Sort items
        try:
            # Try numeric sort first
            items.sort(key=lambda x: float(x[0]) if x[0] and x[0] != 'nan' else float('-inf'), reverse=reverse)
        except (ValueError, TypeError):
            # Fall back to string sort
            items.sort(key=lambda x: str(x[0]).lower(), reverse=reverse)

        # Rearrange items in sorted positions
        for index, (val, child) in enumerate(items):
            self.tree.move(child, '', index)
            # Update row colors
            tag = 'oddrow' if index % 2 else 'evenrow'
            self.tree.item(child, tags=(tag,))

        # Update sort direction for next click
        self.sort_reverse[col] = not reverse

        # Clear arrows from all column headings first
        # Clear arrow from the tree column (#0)
        tree_heading_text = self.tree.heading("#0")["text"]
        if tree_heading_text:
            base_text = tree_heading_text.rstrip(" ↑↓")
            self.tree.heading("#0", text=base_text)

        # Clear arrows from all other columns
        for column in self.columns:
            heading_text = self.tree.heading(column)["text"]
            if heading_text:
                base_text = heading_text.rstrip(" ↑↓")
                self.tree.heading(column, text=base_text)

        # Update current column heading to show sort direction
        heading_text = self.tree.heading(col)["text"]
        if heading_text:
            base_text = heading_text.rstrip(" ↑↓")
            arrow = " ↓" if reverse else " ↑"
            self.tree.heading(col, text=base_text + arrow)

    def _export_csv(self):
        """Export current table data to CSV file"""
        if self.current_data is None or self.current_data.empty:
            messagebox.showwarning("Export CSV", "No data to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save CSV file",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Create a copy of the data with node names as a column
                export_data = self.current_data.copy()
                export_data.insert(0, 'Node', export_data.index)
                export_data.to_csv(file_path, index=False)
                messagebox.showinfo("Export CSV", f"Data exported successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export CSV:\n{str(e)}")

    def clear(self):
        """Clear all items from the treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.current_data = None

    def populate(self, df: pd.DataFrame):
        """Populate the treeview with data from DataFrame"""
        self.clear()
        self.current_data = df.copy()
        
        if df.empty:
            return
        
        # Update columns dynamically based on DataFrame
        new_columns = list(df.columns)
        if new_columns != list(self.columns):
            self.columns = tuple(new_columns)
            self.tree.configure(columns=self.columns)
            
            # Configure column headings and sorting
            for col in self.columns:
                self.tree.heading(col, text=col, 
                                command=lambda c=col: self._sort_column(c, self.sort_reverse.get(c, False)))
                self.tree.column(col, width=120, anchor=tk.W, stretch=True)
                self.sort_reverse[col] = False
        
        # Populate data
        import numpy as np
        for idx, (node, row) in enumerate(df.iterrows()):
            values = []
            for col in self.columns:
                val = row.get(col, np.nan)
                if pd.isna(val):
                    values.append("N/A")
                elif isinstance(val, (int, float)):
                    values.append(f"{val:.6f}")
                else:
                    values.append(str(val))
            
            tag = 'oddrow' if idx % 2 else 'evenrow'
            self.tree.insert("", tk.END, text=str(node), values=values, tags=(tag,))