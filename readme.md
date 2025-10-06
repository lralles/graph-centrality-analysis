## Graph Centrality Impacts Analyser

This program takes a tsv file that describes a graph and performs analysis on how it reacts to node removals in terms of centrality impacts.

The workflow is:
- The user selects the file that describes a graph.
- The user specifies what columns from the tsv represents the edge weight, source and destination nodes. 
- The program shows a preview of the graph
- The user specifies what node it wants to remove and what centrality it wants analysed and if self edges should be included.
- The user runs the analysis.
- The program shows table view shows the result 
- The program shows a view of the graph is loaded highlighting the impact

### Run

```
python3 -m src.application.main
``` 

### Compile 

``` 
pyinstaller --onefile src/application/main.py --hidden-import=matplotlib.backends.backend_svg --hidden-import=PIL._tkinter_finder --paths=. 
```

#### Run Compiled Version

Before running, ensure the executable has the necessary permisions, refer to the chmod command on linux.

```
./dist/main
``` 
