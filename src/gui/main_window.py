import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

from src.gui.toolbar_view import ToolbarView
from src.gui.table_view import TableView
from src.gui.plot_view import PlotView
from src.gui.status_bar_view import StatusBarView
from src.gui.plot_renderer import PlotRenderer
from src.controllers.graph_analysis_controller import GraphAnalysisController
from src.models.graph_loader import GraphLoader
from src.models.centrality_service import CentralityAnalysisService
from src.models.layout_cache import LayoutCache
from src.models.centrality_service import centrality_functions


class GraphAnalysisGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Graph Node Removal Analysis")
        self.geometry("1100x700")

        self._init_style()
        self._build_widgets()

        self.pos_cache = {}
        self.last_save_dir = "."

        self._controller = GraphAnalysisController(
            app=self,
            loader=GraphLoader(),
            analysis=CentralityAnalysisService(),
            layout_cache=LayoutCache(),
            renderer=PlotRenderer(LayoutCache()),
        )

    def _init_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        bg = "#1e1e1e"
        panel_bg = "#252526"
        fg = "#dddddd"
        subtle = "#2d2d30"

        self.configure(background=bg)

        style.configure("TFrame", background=bg)
        style.configure("TPanedwindow", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TButton", background=panel_bg, foreground=fg, padding=(10, 6))
        style.map("TButton", background=[("active", "#3a3d41")])

        style.configure("Tall.TEntry", fieldbackground=panel_bg, foreground=fg, padding=(10, 6))
        style.configure("Tall.TButton", background=panel_bg, foreground=fg, padding=(10, 6))
        style.configure("TEntry", fieldbackground=panel_bg, foreground=fg)

        style.configure(
            "Treeview",
            background=panel_bg,
            fieldbackground=panel_bg,
            foreground=fg,
            rowheight=24,
            font=("Segoe UI", 10),
            bordercolor=subtle,
            lightcolor=subtle,
            darkcolor=subtle,
        )
        style.configure("Treeview.Heading", background=subtle, foreground=fg, font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#094771")], foreground=[("selected", "#ffffff")])
        style.configure("Sash", background=subtle)

    def _build_widgets(self):
        self.toolbar = ToolbarView(self, list(centrality_functions.keys()))
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.toolbar.browse_button.configure(command=self._browse_file)
        self.toolbar.run_button.configure(command=self._on_run)
        self.toolbar.save_button.configure(command=self._on_save_as)
        self.toolbar.clear_button.configure(command=self._on_clear)

        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.table = TableView(paned)
        paned.add(self.table, weight=1)

        self.plot = PlotView(paned)
        paned.add(self.plot, weight=1)

        self.status = StatusBarView(self)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def _browse_file(self):
        path = filedialog.askopenfilename(title="Select graph TSV", filetypes=[("TSV files", "*.tsv"), ("All files", "*.*")])
        if path:
            self.toolbar.file_var.set(path)

    def _on_run(self):
        thread = threading.Thread(target=self._run_analysis_safe)
        thread.daemon = True
        thread.start()

    def _on_save_as(self):
        try:
            path = filedialog.asksaveasfilename(
                title="Save SVG",
                defaultextension=".svg",
                filetypes=[("SVG", "*.svg")],
                initialdir=self.last_save_dir,
                initialfile="Read from TSV.svg",
            )
            if not path:
                return

            self.last_save_dir = os.path.dirname(path)
            file_path = self.toolbar.file_var.get().strip()
            if not file_path:
                messagebox.showwarning("Save SVG", "Run an analysis first.")
                return
            self.plot.figure.savefig(path, dpi=300, bbox_inches='tight', facecolor='white', format='svg')
            self.status.set_status(f"Saved: {path}")
        except Exception as e:
            messagebox.showerror("Save SVG", str(e))

    def _on_clear(self):
        self.table.clear()
        self.plot.clear()
        self.status.set_status("Cleared")

    def _run_analysis_safe(self):
        try:
            self.status.set_status("Running analysis...")
            self._run_analysis()
            self.status.set_status("Done")
        except Exception as e:
            self.status.set_status("Error")
            messagebox.showerror("Error", str(e))

    def _run_analysis(self):
        self._controller.run_analysis()


