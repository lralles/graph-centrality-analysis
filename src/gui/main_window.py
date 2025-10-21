import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import pandas as pd

from src.gui.toolbar_view import ToolbarView
from src.gui.table_view import TableView
from src.gui.plot_view import PlotView
from src.gui.plot_renderer import PlotRenderer
from src.controllers.graph_analysis_controller import GraphAnalysisController
from src.models.graph_loader import GraphLoader
from src.models.centrality_service import CentralityAnalysisService
from src.models.layout_cache import LayoutCache
from src.models.centrality_service import centrality_functions


class GraphAnalysisGUI(tk.Tk):
    def __init__(self):
        """
        Initializes the GUI
        Binds the controller, which handles UI events
        """
        # start Tkinter
        super().__init__()
        self.title("Graph Node Removal Analysis")
        self.geometry("1400x960")

        # build gui
        self._init_style()
        self._build_widgets()

        # initialize program "backend"
        self.pos_cache = {}
        self.last_save_dir = "."
        self.last_analysis_result = None  # Store the last analysis result

        # bind controller - maps gui events to handlers
        self._controller = GraphAnalysisController(
            app=self,
            loader=GraphLoader(),
            analysis=CentralityAnalysisService(),
            layout_cache=LayoutCache(),
            renderer=PlotRenderer(LayoutCache()),
        )

    def _init_style(self):
        """
        Initializes the global styles of the widgets, sets colors and common configs
        """
        # create style object
        style = ttk.Style(self)
        style.theme_use("clam")

        # define a few colors
        bg = "#cccccc"          # background - light grey
        panel_bg = "#dddddd"    # lighter grey
        fg = "#000000"          # black for fonts
        subtle = "#dddddd"      # lighter grey for borders

        # general configurations
        self.configure(background=bg)

        # frame and container style config
        style.configure("TFrame", background=bg)
        style.configure("TPanedwindow", background=bg)

        # data user inputs style config
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TButton", background=panel_bg, foreground=fg, padding=(10, 6))
        style.map("TButton", background=[("active", "#3a3d41")])
        # for tall variants
        style.configure("Tall.TEntry", fieldbackground=panel_bg, foreground=fg, padding=(10, 6))
        style.configure("Tall.TButton", background=panel_bg, foreground=fg, padding=(10, 6))
        style.configure("TEntry", fieldbackground=panel_bg, foreground=fg)

        # combobox elements style config
        style.configure("Tall.TCombobox", fieldbackground=panel_bg, foreground=fg, padding=(10, 6))
        style.configure("TCombobox", fieldbackground=panel_bg, foreground=fg, background=panel_bg)
        style.map("TCombobox",
                  fieldbackground=[("readonly", panel_bg)],
                  selectbackground=[("readonly", panel_bg)],
                  selectforeground=[("readonly", fg)])

        # treeview style config - useful for results table
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

        # divider style config
        style.configure("Sash", background=subtle)

    def _build_widgets(self):
        """
        Initializes the visual elements of the GUI and binds UI events to handlers
        """
        # toolbar initialization, binds events
        self.toolbar = ToolbarView(self, list(centrality_functions.keys()))
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.toolbar.browse_button.configure(command=self._browse_file)
        self.toolbar.run_button.configure(command=self._on_run)
        self.toolbar.refresh_plot_button.configure(command=self._on_refresh_plot)
        self.toolbar.save_button.configure(command=self._on_save_as)
        self.toolbar.clear_button.configure(command=self._on_clear)
        self.toolbar.set_column_selected_callback(self._on_column_selected)

        # Access status bar through toolbar
        self.status = self.toolbar.status_bar

        # paned is the lower panel
        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Create a container frame for the left panel (to switch between views)
        self.left_panel_container = ttk.Frame(paned)
        paned.add(self.left_panel_container, weight=1)

        # Import the adjacency list view
        from src.gui.adjacency_list_view import AdjacencyListView

        # Create both views but only show one at a time
        self.adjacency_list = AdjacencyListView(self.left_panel_container)
        self.table = TableView(self.left_panel_container)

        # Initially show nothing (will show adjacency list after preview)
        # Both views will be packed/unpacked as needed

        # creates the plot visualization
        self.plot = PlotView(paned)
        paned.add(self.plot, weight=1)

        # Note: Status bar has been moved to the toolbar header.

    def _show_adjacency_list(self):
        """Show the adjacency list view and hide the analysis table"""
        self.table.pack_forget()
        self.adjacency_list.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _show_analysis_table(self):
        """Show the analysis table and hide the adjacency list"""
        self.adjacency_list.pack_forget()
        self.table.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _browse_file(self):
        """
        Opens a file dialog and allows user to get file
        """
        # open dialog
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
            # displays file name is toolbar
            self.toolbar.file_var.set(path)

            # gets file extensior
            _, ext = os.path.splitext(path)
            ext = ext.lower()

            if ext == ".tsv" or ext == ".cys":
                self._handle_file_upload(path)
            else:
                self.status.set_status("Selected file type not recognized for column extraction")

    def _handle_file_upload(self, path):
        """
        Handles input of TSV or CYS files
        for TSV: gets columns names and allows user to configure graph on UI
        for CYS: reads graph from file and loads preview, disables column selections
        """
        try:
            file_ext = os.path.splitext(path)[1].lower()

            if file_ext == '.cys':
                self.toolbar.update_column_suggestions([])
                self.toolbar.disable_column_selection()
                self.toolbar.hide_tsv_options()  # Hide TSV-specific options for CYS files

                loader = GraphLoader()
                networks = loader.get_available_networks(path)

                if networks:
                    self.toolbar.update_network_list(networks)
                    self.status.set_status(f"Loaded .cys file with {len(networks)} network(s)")
                else:
                    self.toolbar.hide_network_selector()
                    self.status.set_status("Loaded .cys file")

                # avoid unbind bugs (method called while constructor is executing)
                if hasattr(self, '_controller'):
                    self.after(100, self._controller.generate_preview)
            else:
                # Hide network selector for non-.cys files
                self.toolbar.hide_network_selector()
                self.toolbar.show_tsv_options()  # Show TSV-specific options for TSV files

                df = pd.read_csv(path, sep='\t', nrows=0)
                columns = df.columns.tolist()
                self.toolbar.update_column_suggestions(columns)
                self.toolbar.enable_column_selection()
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
        self.adjacency_list.clear()
        self.plot.clear()
        self.toolbar.clear_node_selector()
        self.toolbar.hide_tsv_options()  # Hide TSV options when clearing
        self.toolbar.hide_network_selector()  # Hide network selector when clearing
        self.last_analysis_result = None
        # Hide both views when clearing
        self.table.pack_forget()
        self.adjacency_list.pack_forget()
        # Expand the configuration section when clearing to allow new configuration
        self.toolbar.expand()
        self.status.set_status("Cleared")

    def _run_analysis_safe(self):
        try:
            self.status.set_status("Running analysis...")
            self._run_analysis()
            self.status.set_status("Done")
            self._on_refresh_plot()
            # Auto-collapse the configuration section after successful analysis
            self.toolbar.collapse()
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
            "layout_type": self.toolbar.layout_type_var.get(),
        }

        self._controller.renderer.render(self.plot.figure, self.last_analysis_result, plot_options)
        self.plot.draw_idle()


