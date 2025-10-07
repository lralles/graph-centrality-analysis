import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import pandas as pd

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
        self.last_analysis_result = None  # Store the last analysis result

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

        # Combobox styles
        style.configure("Tall.TCombobox", fieldbackground=panel_bg, foreground=fg, padding=(10, 6))
        style.configure("TCombobox", fieldbackground=panel_bg, foreground=fg, background=panel_bg)
        style.map("TCombobox",
                  fieldbackground=[("readonly", panel_bg)],
                  selectbackground=[("readonly", panel_bg)],
                  selectforeground=[("readonly", fg)])

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
        self.toolbar.refresh_plot_button.configure(command=self._on_refresh_plot)
        self.toolbar.save_button.configure(command=self._on_save_as)
        self.toolbar.clear_button.configure(command=self._on_clear)
        self.toolbar.set_column_selected_callback(self._on_column_selected)

        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.table = TableView(paned)
        paned.add(self.table, weight=1)

        self.plot = PlotView(paned)
        paned.add(self.plot, weight=1)

        self.status = StatusBarView(self)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="Select graph file",
            filetypes=[
                ("Graph files", "*.tsv *.cys"),
                ("TSV files", "*.tsv"),
                ("Cytoscape files", "*.cys"),
                ("All files", "*.*")
            ]
        )
        if path:
            self.toolbar.file_var.set(path)
            # Read file to get column names for autocomplete (TSV) or disable column selection (CYS)
            _, ext = os.path.splitext(path)
            ext = ext.lower()
            if ext == ".tsv":
                self._load_column_names(path)
            elif ext == ".cys":
                # Cytoscape session file - column selection not applicable
                try:
                    self.toolbar.update_column_suggestions([])
                except Exception:
                    pass
                self.status.set_status("CYS file selected; column selection disabled")
            else:
                # For other file types, attempt to load columns (best-effort)
                try:
                    self._load_column_names(path)
                except Exception:
                    # If loading fails, clear suggestions
                    try:
                        self.toolbar.update_column_suggestions([])
                    except Exception:
                        pass
                    self.status.set_status("Selected file type not recognized for column extraction")

    def _load_column_names(self, path):
        """Load column names from TSV file and update autocomplete suggestions, or handle .cys files"""
        try:
            file_ext = os.path.splitext(path)[1].lower()

            if file_ext == '.cys':
                # For .cys files, disable column selection and show info
                try:
                    self.toolbar.update_column_suggestions([])
                except Exception:
                    pass

                # Attempt to disable column selection UI if available
                try:
                    self.toolbar.disable_column_selection()
                except Exception:
                    pass

                # Get available networks in the .cys file (best-effort)
                try:
                    loader = GraphLoader()
                    networks = loader.get_available_networks(path)
                except Exception:
                    networks = None

                if networks:
                    self.status.set_status(f"Loaded .cys file with {len(networks)} network(s)")
                else:
                    self.status.set_status("Loaded .cys file")
            else:
                # For TSV and other tabular files, read column names
                df = pd.read_csv(path, sep='\t', nrows=0)
                columns = df.columns.tolist()
                try:
                    self.toolbar.update_column_suggestions(columns)
                except Exception:
                    pass
                # Attempt to enable column selection UI if available
                try:
                    self.toolbar.enable_column_selection()
                except Exception:
                    pass
                self.status.set_status(f"Loaded {len(columns)} columns from file")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{str(e)}")

    def _on_column_selected(self):
        """Called when a column is selected - trigger preview generation"""
        if hasattr(self, '_controller'):
            self._controller.generate_preview()

    def _on_run(self):
        thread = threading.Thread(target=self._run_analysis_safe)
        thread.daemon = True
        thread.start()

    def _on_refresh_plot(self):
        """Refresh the plot with current options without re-running analysis"""
        if self.last_analysis_result is None:
            messagebox.showwarning("Refresh Plot", "Please run an analysis first.")
            return

        try:
            self.status.set_status("Refreshing plot...")
            self._render_plot()
            self.status.set_status("Plot refreshed")
        except Exception as e:
            messagebox.showerror("Refresh Plot Error", str(e))
            self.status.set_status("Error refreshing plot")

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
        self.last_analysis_result = None
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

    def _render_plot(self):
        """Render the plot with current plot options"""
        if self.last_analysis_result is None:
            return

        plot_options = {
            "show_node_names": self.toolbar.show_node_names_var.get(),
            "edge_thickness_by_weight": self.toolbar.edge_thickness_by_weight_var.get(),
            "mark_removed_edges": self.toolbar.mark_removed_edges_var.get(),
        }

        self._controller.renderer.render(self.plot.figure, self.last_analysis_result, plot_options)
        self.plot.draw_idle()


