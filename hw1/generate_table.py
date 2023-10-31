import re
import pandas as pd

def extract_metrics_from_file(file_path):
    metrics = {
        "Eval_StdReturn": [],
        "Eval_MaxReturn": [],
        "Eval_MinReturn": [],
        "Eval_AverageEpLen": [],
        "Train_AverageReturn": [],
        "Train_StdReturn": [],
        "Train_MaxReturn": [],
        "Train_MinReturn": [],
        "Train_AverageEpLen": [],
        "Training Loss": [],
        "Train_EnvstepsSoFar": [],
        "TimeSinceStart": [],
        "Initial_DataCollection_AverageReturn": []
    }

    with open(file_path, 'r') as file:
        for line in file:
            for metric in metrics.keys():
                if metric in line:
                    value = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                    if value:
                        metrics[metric].append(float(value[0]))
    
    return metrics

def generate_table(metrics):
    df = pd.DataFrame(metrics)
    return df

file_path = 'training_output.txt'  # Change this to your file path
metrics = extract_metrics_from_file(file_path)
table = generate_table(metrics)

print(table)
