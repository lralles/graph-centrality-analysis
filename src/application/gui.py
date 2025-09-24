from src.gui.main_window import GraphAnalysisGUI as _GraphAnalysisGUI


# Compatibility shim: re-export main window class
class GraphAnalysisGUI(_GraphAnalysisGUI):
    pass


