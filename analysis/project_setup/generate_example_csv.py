"""
This file is used to produce an example patient-level data to support developing analysis script.

To use, run this in terminal: python analysis/project_setup/generate_example_csv.py
"""

import os
import pandas as pd

cwd = os.getcwd()
print(f"Current working directory: {cwd}")

input_path = "./output/dataset_patients_combined.csv.gz"
output_path = "example/dataset_patients_example.csv"
date_col = "index_date"

# input_path = "./output/dataset_practices.csv.gz"
# output_path = "example/dataset_practices_example.csv"
# date_col = "interval_start"

# df = pd.read_csv(input_path)
# Save example dataset
df = pd.read_csv(input_path)

# Convert index date to datetime
df[date_col] = pd.to_datetime(df[date_col])

# Take the first 10 rows from each month
example_df = (
    df.sort_values(date_col)
    .groupby(date_col, group_keys=False)
    .head(10)
)

# Create example folder if it does not already exist
# os.makedirs("example", exist_ok=True)

example_df.to_csv(
    output_path,
    index=False,
)

print(f"Example dataset saved to: {output_path}")
print(f"Number of rows: {len(example_df):,}")
print(f"Number of months: {example_df[date_col].nunique():,}")

print(example_df.head())