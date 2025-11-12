import networkx as nx

def make_graph(
    graph_type: str,
    size: int,
    seed: int = 42,
) -> nx.Graph:
    """
    Generate a random graph of the specified type and size.
    
    Args:
        graph_type: Type of graph to generate ('erdos_renyi', 'barabasi_albert', 'watts_strogatz')
        size: Number of nodes in the graph
        seed: Random seed for reproducibility
        
    Returns:
        NetworkX Graph object
    """
    if graph_type == "erdos_renyi":
        c = 5
        p = c / size
        G = nx.erdos_renyi_graph(size, p, seed=seed, directed=False)
    
    elif graph_type == "barabasi_albert":
        m = max(2, size // 50)
        G = nx.barabasi_albert_graph(size, m, seed=seed)
    
    elif graph_type == "watts_strogatz":
        k = max(2, size // 50)
        G = nx.watts_strogatz_graph(size, k, 0.3, seed=seed)
    else:
        raise ValueError(f"Unsupported graph_type: {graph_type}")

    return G


def get_available_graph_types():
    """
    Get list of available random graph types.
    
    Returns:
        List of graph type names
    """
    return ["erdos_renyi", "barabasi_albert", "watts_strogatz"]


def get_graph_type_display_names():
    """
    Get mapping of graph types to display names.
    
    Returns:
        Dictionary mapping graph types to display names
    """
    return {
        "erdos_renyi": "Erdős-Rényi",
        "barabasi_albert": "Barabási-Albert", 
        "watts_strogatz": "Watts-Strogatz"
    }