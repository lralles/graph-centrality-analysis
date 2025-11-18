# Getting Started

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
python3 -m src.application.main
```

## First Launch

When you start the application, it automatically loads a random Watts-Strogatz graph with 100 nodes. This allows you to immediately explore the features without needing your own data.

## Interface Overview

The main window contains:

- **Toolbar**: File operations, analysis controls, and options
- **Graph View**: Visual representation of the network
- **Table View**: Analysis results in tabular format
- **Adjacency List**: Text representation of graph structure
- **Status Bar**: Progress updates and current operation status

## Basic Navigation

- Use the toolbar buttons to load files or generate random graphs
- Select if you want to remove the zero degree nodes or use the largest component only
- Explore your network on the preview mode
- Select centrality measures from the options
- Use the node selection to choose which nodes to remove
- Click "Run Analysis" to perform the centrality impact analysis

## Getting Help

- Check the status bar for current operation feedback
- Refer to this documentation for detailed feature explanations