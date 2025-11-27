import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import glob
import os

# Set style for better-looking plots
plt.style.use('default')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

def load_benchmark_data(csv_pattern="benchmark_results_*.csv"):
    """
    Load benchmark data from CSV files matching the pattern.
    
    Args:
        csv_pattern: Pattern to match CSV files
        
    Returns:
        pandas.DataFrame: Combined benchmark data
    """
    # Look for CSV files in the project root
    project_root = Path(__file__).parent.parent.parent
    csv_files = glob.glob(str(project_root / csv_pattern))
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found matching pattern: {csv_pattern}")
    
    # Load and combine all CSV files
    dataframes = []
    for file in csv_files:
        df = pd.read_csv(file)
        df['source_file'] = os.path.basename(file)
        dataframes.append(df)
    
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Filter out rows with errors (where mean_time is null)
    combined_df = combined_df.dropna(subset=['mean_time'])
    
    return combined_df

def plot_scaling_behavior(df, save_path=None):
    """
    Plot how execution time scales with graph size for each centrality measure (log scale).
    """
    plt.figure(figsize=(12, 8))
    
    centralities = df['centrality'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(centralities)))
    
    for i, centrality in enumerate(centralities):
        centrality_data = df[df['centrality'] == centrality].sort_values('nodes')
        plt.plot(centrality_data['nodes'], centrality_data['mean_time'], 
                marker='o', linewidth=2, markersize=6, label=centrality.capitalize(), color=colors[i])
    
    plt.title('Centrality Computation Time vs Graph Size (Log Scale)', fontsize=16, fontweight='bold')
    plt.xlabel('Number of Nodes', fontsize=12)
    plt.ylabel('Execution Time (seconds)', fontsize=12)
    plt.yscale('log')
    plt.xscale('linear')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_scaling_behavior_linear(df, save_path=None):
    """
    Plot how execution time scales with graph size for each centrality measure (linear scale).
    """
    plt.figure(figsize=(12, 8))
    
    centralities = df['centrality'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(centralities)))
    
    for i, centrality in enumerate(centralities):
        centrality_data = df[df['centrality'] == centrality].sort_values('nodes')
        plt.plot(centrality_data['nodes'], centrality_data['mean_time'], 
                marker='o', linewidth=2, markersize=6, label=centrality.capitalize(), color=colors[i])
    
    plt.title('Centrality Computation Time vs Graph Size (Linear Scale)', fontsize=16, fontweight='bold')
    plt.xlabel('Number of Nodes', fontsize=12)
    plt.ylabel('Execution Time (seconds)', fontsize=12)
    plt.yscale('linear')
    plt.xscale('linear')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_time_distributions(df, save_path=None):
    """
    Create box plots showing the distribution of execution times for each centrality.
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    centralities = sorted(df['centrality'].unique())
    
    # Define colors for each graph size
    size_colors = plt.cm.Set3(np.linspace(0, 1, 10))
    
    for i, centrality in enumerate(centralities):
        if i >= len(axes):
            break
            
        centrality_data = df[df['centrality'] == centrality]
        
        # Create a box plot for each graph size
        graph_sizes = sorted(centrality_data['nodes'].unique())
        times_by_size = []
        labels = []
        
        for size in graph_sizes:
            size_data = centrality_data[centrality_data['nodes'] == size]
            if not size_data.empty:
                # Approximate distribution using mean and std
                mean_time = size_data['mean_time'].iloc[0]
                std_time = size_data['std_time'].iloc[0]
                min_time = size_data['min_time'].iloc[0]
                max_time = size_data['max_time'].iloc[0]
                
                # Create approximate data points
                times_by_size.append([min_time, mean_time - std_time, mean_time, 
                                    mean_time + std_time, max_time])
                labels.append(f'{size}')
        
        if times_by_size:
            bp = axes[i].boxplot(times_by_size, tick_labels=labels, patch_artist=True)
            
            # Color the boxes
            for j, patch in enumerate(bp['boxes']):
                patch.set_facecolor(size_colors[j % len(size_colors)])
        
        axes[i].set_title(f'{centrality.capitalize()} Centrality', fontweight='bold')
        axes[i].set_xlabel('Graph Size (nodes)')
        axes[i].set_ylabel('Time (seconds)')
        axes[i].set_yscale('log')
        axes[i].grid(True, alpha=0.3)
    
    # Hide unused subplots
    for i in range(len(centralities), len(axes)):
        axes[i].set_visible(False)

    plt.suptitle('Execution Time Distributions by Centrality and Graph Size',
                fontsize=16, fontweight='bold')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_time_distributions_linear(df, save_path=None):
    """
    Create violin plots showing the distribution of execution times for each centrality (linear scale).
    """
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    centralities = sorted(df['centrality'].unique())

    # Color palette for different centralities
    colors = plt.cm.Set2(np.linspace(0, 1, len(centralities)))

    for i, centrality in enumerate(centralities):
        if i >= len(axes):
            break

        centrality_data = df[df['centrality'] == centrality].sort_values('nodes')

        # Prepare data for violin plot
        graph_sizes = sorted(centrality_data['nodes'].unique())

        # Create scatter plot with error bars
        x_pos = []
        y_means = []
        y_errors = []

        for j, size in enumerate(graph_sizes):
            size_data = centrality_data[centrality_data['nodes'] == size]
            if not size_data.empty:
                mean_time = size_data['mean_time'].iloc[0]
                std_time = size_data['std_time'].iloc[0]
                min_time = size_data['min_time'].iloc[0]
                max_time = size_data['max_time'].iloc[0]

                x_pos.append(size)
                y_means.append(mean_time)
                y_errors.append(std_time)

                # Add individual data points with jitter
                axes[i].scatter([size] * 3, [min_time, mean_time, max_time],
                              alpha=0.6, s=30, color=colors[i])

        # Plot mean with error bars
        if x_pos:
            axes[i].errorbar(x_pos, y_means, yerr=y_errors,
                           fmt='o-', linewidth=2, markersize=8,
                           color=colors[i], capsize=5, capthick=2,
                           label=f'{centrality.capitalize()}')

            # Fill area between min and max
            for j, size in enumerate(x_pos):
                size_data = centrality_data[centrality_data['nodes'] == size]
                if not size_data.empty:
                    min_time = size_data['min_time'].iloc[0]
                    max_time = size_data['max_time'].iloc[0]
                    axes[i].fill_between([size-50, size+50], [min_time, min_time],
                                       [max_time, max_time], alpha=0.2, color=colors[i])

        axes[i].set_title(f'{centrality.capitalize()} Centrality', fontweight='bold', fontsize=14)
        axes[i].set_xlabel('Graph Size (nodes)', fontsize=12)
        axes[i].set_ylabel('Time (seconds)', fontsize=12)
        axes[i].set_yscale('linear')
        axes[i].set_xscale('linear')
        axes[i].grid(True, alpha=0.3)
        axes[i].tick_params(axis='both', which='major', labelsize=10)

    # Hide unused subplots
    for i in range(len(centralities), len(axes)):
        axes[i].set_visible(False)

    plt.suptitle('Execution Time Distributions by Centrality and Graph Size (Linear Scale)',
                fontsize=16, fontweight='bold')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def generate_all_plots(csv_pattern="benchmark_results_*.csv", save_plots=False):
    """
    Generate all visualization plots for the benchmark data.

    Args:
        csv_pattern: Pattern to match CSV files
        save_plots: Whether to save plots to files
    """
    print("Loading benchmark data...")
    df = load_benchmark_data(csv_pattern)

    print(f"Loaded {len(df)} benchmark records")
    print(f"Centralities: {', '.join(df['centrality'].unique())}")
    print(f"Graph sizes: {', '.join(map(str, sorted(df['nodes'].unique())))}")
    print()

    save_dir = Path(__file__).parent / "plots" if save_plots else None
    if save_dir:
        save_dir.mkdir(exist_ok=True)

    print("Generating plots...")

    # 1. Scaling behavior (log scale)
    print("1. Scaling behavior (log scale)...")
    plot_scaling_behavior(df, save_dir / "scaling_behavior_log.svg" if save_dir else None)

    # 2. Scaling behavior (linear scale)
    print("2. Scaling behavior (linear scale)...")
    plot_scaling_behavior_linear(df, save_dir / "scaling_behavior_linear.svg" if save_dir else None)

    # 3. Time distributions (linear scale)
    print("4. Time distributions (linear scale)...")
    plot_time_distributions_linear(df, save_dir / "time_distributions_linear.svg" if save_dir else None)

    print("All plots generated!")

    if save_plots:
        print(f"Plots saved to: {save_dir}")

if __name__ == "__main__":
    # Generate all plots
    generate_all_plots(save_plots=True)