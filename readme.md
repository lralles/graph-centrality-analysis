This program takes a tsv file that describes a graph and performs analysis on how it reacts to node removals in terms of centrality impacts.

Compile 

pyinstaller --onefile src/application/main.py --hidden-import=matplotlib.backends.backend_svg --hidden-import=PIL._tkinter_finder --paths=.

run

python3 -m src.application.main