import time
import statistics
from typing import Dict, List
import sys
import os
import csv
from datetime import datetime

# Add the src directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.random_graph_generator import make_graph
from models.centrality_service import CentralityAnalysisService


def benchmark_centrality_service(graph, centralities: List[str], runs: int = 10) -> Dict:
    """
    Benchmark centrality computation using the CentralityAnalysisService.

    Args:
        graph: NetworkX graph
        centralities: List of centrality measures to compute
        runs: Number of times to run the benchmark

    Returns:
        Dictionary with timing statistics for each centrality
    """
    service = CentralityAnalysisService()
    results = {}

    # Select a node to remove (use the first node)
    nodes_to_remove = [list(graph.nodes())[0]] if graph.number_of_nodes() > 0 else []

    for centrality in centralities:
        times = []
        errors = []

        for run_num in range(runs):
            start_time = time.time()
            try:
                # Remove one node and compute centrality
                service.compute(graph, nodes_to_remove, [centrality])
                end_time = time.time()
                times.append(end_time - start_time)
            except Exception as e:
                error_msg = f"Run {run_num + 1}: {type(e).__name__}: {str(e)}"
                errors.append(error_msg)
                print(f"Error computing {centrality} (run {run_num + 1}): {e}")
        
        # If all runs failed, return error result
        if not times:
            full_error_msg = "; ".join(errors)
            results[centrality] = {
                'centrality': centrality,
                'error': full_error_msg,
                'mean_time': None,
                'std_time': None,
                'min_time': None,
                'max_time': None,
                'successful_runs': 0,
                'failed_runs': len(errors)
            }
        else:
            # If some runs failed, include partial error info
            error_info = ""
            if errors:
                error_info = f"Partial failures: {len(errors)}/{runs} runs failed - {'; '.join(errors[:3])}"
                if len(errors) > 3:
                    error_info += f" (and {len(errors) - 3} more)"
            
            results[centrality] = {
                'centrality': centrality,
                'mean_time': statistics.mean(times),
                'std_time': statistics.stdev(times) if len(times) > 1 else 0,
                'min_time': min(times),
                'max_time': max(times),
                'all_times': times,
                'error': error_info,
                'successful_runs': len(times),
                'failed_runs': len(errors)
            }
    
    return results


def save_results_to_csv(size: int, results: Dict, filename: str = "benchmark_results.csv"):
    """
    Save benchmark results to CSV file.
    
    Args:
        size: Graph size
        results: Dictionary of benchmark results by centrality
        filename: CSV filename
    """
    file_exists = os.path.exists(filename)
    
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'graph_size', 'nodes', 'edges', 'centrality', 'mean_time', 
                     'std_time', 'min_time', 'max_time', 'successful_runs', 'failed_runs', 'error']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        timestamp = datetime.now().isoformat()
        
        for centrality, result in results.items():
            writer.writerow({
                'timestamp': timestamp,
                'graph_size': size,
                'nodes': result.get('nodes', size),
                'edges': result.get('edges', 0),
                'centrality': result['centrality'],
                'mean_time': result.get('mean_time'),
                'std_time': result.get('std_time'),
                'min_time': result.get('min_time'),
                'max_time': result.get('max_time'),
                'successful_runs': result.get('successful_runs', 0),
                'failed_runs': result.get('failed_runs', 0),
                'error': result.get('error', '')
            })


def run_benchmarks():
    """
    Run benchmarks for all centrality measures on different graph sizes.
    """
    # Graph sizes to test
    sizes = [2000, 3000, 5000]
    
    # Centrality measures to benchmark
    centralities_to_test = ['degree', 'katz', 'eigenvector', 'betweenness', 'closeness']
    
    csv_filename = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    print("Graph Centrality Benchmarks")
    print("=" * 50)
    print(f"Results will be saved to: {csv_filename}")
    print()
    
    for size in sizes:
        print(f"Graph Size: {size} nodes")
        print("-" * 30)
        
        # Generate Erdős-Rényi graph
        graph = make_graph("erdos_renyi", size, seed=42)
        nodes = graph.number_of_nodes()
        edges = graph.number_of_edges()
        print(f"Generated graph with {nodes} nodes and {edges} edges")
        
        print(f"Running centrality benchmarks (10 runs each)...")
        
        # Run benchmarks for all centralities
        results = benchmark_centrality_service(graph, centralities_to_test, runs=10)
        
        # Add graph info to results
        for centrality in results:
            results[centrality]['nodes'] = nodes
            results[centrality]['edges'] = edges
        
        # Print results
        for centrality_name in centralities_to_test:
            result = results.get(centrality_name, {})
            if result.get('error') and result.get('mean_time') is None:
                print(f"{centrality_name.capitalize():>12}: ERROR - {result['error']}")
            elif result.get('error'):
                print(f"{centrality_name.capitalize():>12}: {result['mean_time']:.4f}s ± {result['std_time']:.4f}s "
                      f"(min: {result['min_time']:.4f}s, max: {result['max_time']:.4f}s) - {result['error']}")
            else:
                print(f"{centrality_name.capitalize():>12}: {result['mean_time']:.4f}s ± {result['std_time']:.4f}s "
                      f"(min: {result['min_time']:.4f}s, max: {result['max_time']:.4f}s)")
        
        # Save results for this graph size to CSV
        save_results_to_csv(size, results, csv_filename)
        print(f"\nResults for size {size} saved to {csv_filename}")
        
        print()
        
        # Summary for this size
        valid_results = [r for r in results.values() if not r.get('error') or r.get('mean_time') is not None]
        if valid_results:
            fastest = min(valid_results, key=lambda x: x['mean_time'])
            slowest = max(valid_results, key=lambda x: x['mean_time'])
            print(f"Fastest: {fastest['centrality']} ({fastest['mean_time']:.4f}s)")
            print(f"Slowest: {slowest['centrality']} ({slowest['mean_time']:.4f}s)")
            print(f"Speed ratio: {slowest['mean_time'] / fastest['mean_time']:.2f}x")
        
        print()
        print("=" * 50)
        print()
    
    print(f"All benchmarks completed! Results saved to: {csv_filename}")


if __name__ == "__main__":
    run_benchmarks()