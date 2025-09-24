import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PlotView(ttk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

    def clear(self):
        self.figure.clf()
        self.canvas.draw_idle()

    def draw_idle(self):
        self.canvas.draw_idle()


