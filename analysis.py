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
