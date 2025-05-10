import os
import json
import numpy as np

def load_metrics_from_files():
    metrics = {
        'answer_relevancy': [],
        'answer_correctness': [], 
        'semantic_similarity': []
    }
    
    for file in os.listdir('QnA'):
        if not file.startswith('file_eval') or not file.endswith('.json'):
            continue
            
        with open(f'QnA/{file}', 'r') as f:
            data = json.loads(f.read())
            for entry in data:
                for metric in metrics.keys():
                    value = entry.get(metric)
                    if value and not np.isnan(value):
                        metrics[metric].append(value)
                        
    return metrics

def calculate_statistics(metrics):
    stats = {}
    for metric, values in metrics.items():
        if values:
            # Sort values in descending order
            values_array = np.array(values)
            # For decreasing order, we want the highest values, so we use 100 minus the percentile
            stats[metric] = {
                'p90': np.percentile(values_array, 100-90),  # Top 90%
                'p95': np.percentile(values_array, 100-95),  # Top 95%
                'p99': np.percentile(values_array, 100-99),  # Top 99%
                'avg': np.mean(values_array)
            }
    return stats


def plot_metric_histograms(metrics):
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Set the style to a default matplotlib style
    plt.style.use('default')
    
    # Create a figure with subplots for each metric
    fig, axes = plt.subplots(len(metrics), 1, figsize=(12, 5*len(metrics)))
    fig.suptitle('Distribution of Metrics', fontsize=16, y=1.02)
    
    # If there's only one metric, axes will not be an array
    if len(metrics) == 1:
        axes = [axes]
    
    for ax, (metric_name, values) in zip(axes, metrics.items()):
        if values:
            # Create histogram with a specific color
            sns.histplot(data=values, bins=30, ax=ax, color='skyblue', alpha=0.6, label='Frequency Distribution')
            
            # Add vertical lines for statistics with enhanced visibility
            mean_val = np.mean(values)
            median_val = np.median(values)
            p90 = np.percentile(values, 100-90)  # Top 90%
            p95 = np.percentile(values, 100-95)  # Top 95%
            
            # Add statistical lines with increased width and alpha
            ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, 
                      label=f'Mean: {mean_val:.3f}')
            ax.axvline(median_val, color='green', linestyle='--', linewidth=2, 
                      label=f'Median: {median_val:.3f}')
            ax.axvline(p90, color='purple', linestyle='--', linewidth=2, 
                      label=f'Top 90% threshold: {p90:.3f}')
            ax.axvline(p95, color='orange', linestyle='--', linewidth=2, 
                      label=f'Top 95% threshold: {p95:.3f}')
            
            ax.set_title(f'{metric_name} Distribution', fontsize=14, pad=20)
            ax.set_xlabel('Score', fontsize=12)
            ax.set_ylabel('Count', fontsize=12)
            
            # Add legend with better positioning and formatting
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10,
                     title='Statistics', title_fontsize=12)
            
            # Add grid for better readability
            ax.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('metrics_histograms.png', bbox_inches='tight', dpi=300)
    plt.close()

def plot_metric_correlations(metrics):
    """
    Generate scatter plots to visualize correlations between different metrics.
    
    Args:
        metrics (dict): Dictionary containing metric names and their values
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Get all metric names
    metric_names = list(metrics.keys())
    n_metrics = len(metric_names)
    
    if n_metrics < 2:
        print("Need at least 2 metrics to create correlation plots")
        return
        
    # Create a figure with subplots for each pair of metrics
    n_plots = (n_metrics * (n_metrics - 1)) // 2
    n_cols = min(3, n_plots)
    n_rows = (n_plots + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(6*n_cols, 5*n_rows))
    fig.suptitle('Correlations Between Metrics', fontsize=16, y=1.02)
    
    # Flatten axes array for easier indexing
    if n_plots > 1:
        axes = axes.flatten()
    else:
        axes = [axes]
        
    plot_idx = 0
    # Create scatter plots for each pair of metrics
    for i in range(n_metrics):
        for j in range(i+1, n_metrics):
            if plot_idx < len(axes):
                metric1 = metric_names[i]
                metric2 = metric_names[j]
                
                # Get values, removing any None or missings values
                values1 = [v for v in metrics[metric1] if v is not None]
                values2 = [v for v in metrics[metric2] if v is not None]
                
                # Only plot if we have matching data points
                min_len = min(len(values1), len(values2))
                if min_len > 0:
                    # Calculate correlation coefficient
                    corr = np.corrcoef(values1[:min_len], values2[:min_len])[0,1]
                    
                    # Create scatter plot using sequence for x-axi
                    # s
                    x_seq = list(range(min_len))
                    axes[plot_idx].scatter(x_seq, values2[:min_len], 
                                         alpha=0.5, color='skyblue')
                    axes[plot_idx].set_xlabel('Question Sequence Count', fontsize=10)
                    axes[plot_idx].set_ylabel(metric2, fontsize=10)
                    axes[plot_idx].grid(True, linestyle='--', alpha=0.7)
                
                plot_idx += 1
    
    # Remove any empty subplots
    for idx in range(plot_idx, len(axes)):
        fig.delaxes(axes[idx])
    
    plt.tight_layout()
    plt.savefig('metric_correlations.png', bbox_inches='tight', dpi=300)
    plt.close()


if __name__ == "__main__":
    metrics = load_metrics_from_files()
    stats = calculate_statistics(metrics)
    
    print("\nPercentile Analysis (in decreasing order - higher values are better):")
    for metric, values in stats.items():
        print(f"\n{metric}:")
        print(f"Top 90% (P90): {values['p90']:.3f}")
        print(f"Top 95% (P95): {values['p95']:.3f}")
        print(f"Top 99% (P99): {values['p99']:.3f}")
        print(f"Average: {values['avg']:.3f}")
    #plot_metric_histograms(metrics)
    plot_metric_correlations(metrics)