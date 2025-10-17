import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PlotView(ttk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        # Create figure with minimal padding
        self.figure = Figure(figsize=(5, 4), dpi=100, tight_layout=True)
        # Set figure background to match the widget
        self.figure.patch.set_facecolor('white')

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

    def clear(self):
        # Clear the figure and re-apply the background and tight layout
        self.figure.clf()
        try:
            # re-apply background color after clearing
            self.figure.patch.set_facecolor('white')
            # re-enable tight layout if supported
            if hasattr(self.figure, "set_tight_layout"):
                self.figure.set_tight_layout(True)
        except Exception:
            pass
        self.canvas.draw_idle()

    def draw_idle(self):
        self.canvas.draw_idle()


