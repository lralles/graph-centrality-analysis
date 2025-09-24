import tkinter as tk
from tkinter import ttk

class StatusBarView(ttk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master, padding=(10, 6))
        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(self, textvariable=self.status_var).pack(side=tk.LEFT)

    def set_status(self, text: str):
        self.status_var.set(text)


