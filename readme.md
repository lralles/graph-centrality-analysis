This program takes a tsv file that describes a graph and performs analysis on how it reacts to node removals in terms of centrality impacts.

The workflow is:
- The user selects the file that describes a graph.
- The user specifies what columns from the tsv represents the edge weight, source and destination nodes. 
- The user specifies what node it wants to remove and what centrality it wants analysed and if self edges should be included.
- The user runs the analysis.
- A table view shows the result and a view of the graph is loaded highlighting the impact

Compile 

pyinstaller --onefile src/application/main.py --hidden-import=matplotlib.backends.backend_svg --hidden-import=PIL._tkinter_finder --paths=.

run

python3 -m src.application.main