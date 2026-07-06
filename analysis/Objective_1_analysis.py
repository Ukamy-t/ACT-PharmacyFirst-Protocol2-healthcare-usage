import os
import pandas as pd

cwd = os.getcwd()
print(f"Current working directory: {cwd}")

# Read combined monthly patient dataset
df = pd.read_csv("./output/dataset_patients_combined.csv.gz")

print(df.head())
print(f"Number of rows: {len(df):,}")
print(f"Number of columns: {len(df.columns)}")
for column in df.columns:
    print(column)