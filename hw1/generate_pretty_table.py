from prettytable import PrettyTable
import re

def extract_metrics_from_file(file_path):
    metrics = {
        "Metric": [],
        "Value": []
    }

    # Define the metrics we're interested in
    interested_metrics = ["Eval_StdReturn", "Eval_MaxReturn", "Eval_MinReturn", 
                          "Eval_AverageEpLen", "Train_AverageReturn", "Train_StdReturn", 
                          "Train_MaxReturn", "Train_MinReturn", "Train_AverageEpLen", 
                          "Training Loss", "Train_EnvstepsSoFar", "TimeSinceStart", 
                          "Initial_DataCollection_AverageReturn"]

    with open(file_path, 'r') as file:
        for line in file:
            if any(metric in line for metric in interested_metrics):
                parts = line.split(":")
                if len(parts) == 2:
                    metric_name = parts[0].strip()
                    metric_value = parts[1].strip()
                    metrics["Metric"].append(metric_name)
                    metrics["Value"].append(metric_value)
    
    return metrics

def generate_pretty_table(metrics):
    table = PrettyTable()
    table.field_names = ["Metric", "Value"]
    for metric, value in zip(metrics["Metric"], metrics["Value"]):
        table.add_row([metric, value])

    return table

file_path = 'training_output.txt'  # Change this to the path of your output file
metrics = extract_metrics_from_file(file_path)
pretty_table = generate_pretty_table(metrics)

print(pretty_table)
