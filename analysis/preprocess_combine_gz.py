import pandas as pd
from pathlib import Path
import config
from config import month_range
import argparse

# utilisation: python analysis/preprocess_combine_gz.py

# start_dates = month_range(config.start, config.end)
start_dates = ["2024-02-01", "2024-03-01"]

dfs = []

for d in start_dates:
    file = Path(f"output/dataset_patients_{d}.csv.gz")

    if file.exists():
        df = pd.read_csv(file)
        dfs.append(df)

combined = pd.concat(dfs, ignore_index=True)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--output",
    default="output/dataset_patients_combined.csv.gz",
    help="Output file path"
)

args = parser.parse_args()
combined.to_csv(args.output, index=False)
