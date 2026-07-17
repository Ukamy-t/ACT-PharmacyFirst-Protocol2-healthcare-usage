import argparse
import gzip
from pathlib import Path
import pandas as pd
import config

"""
Combine monthly patient-level datasets into one CSV.GZ file.

The monthly datasets are read in chunks and written directly to the
combined output file, avoiding loading all months into memory.
"""

def combine_monthly_datasets(output_file, chunksize=100_000):
    start_dates = config.month_range(config.start, config.end)

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    first_chunk = True
    expected_columns = None

    total_files = 0
    total_rows = 0

    with gzip.open(output_file, mode="wt", newline="") as output_handle:

        for start_date in start_dates:
            input_file = Path(
                f"output/dataset_patients_{start_date}.csv.gz"
            )

            if not input_file.exists():
                print(
                    f"Warning: file not found: {input_file}",
                    flush=True,
                )
                continue

            print(
                f"Processing: {input_file}",
                flush=True,
            )

            # Read only the header first
            header = pd.read_csv(
                input_file,
                nrows=0,
            )

            current_columns = header.columns.tolist()

            # Check that all monthly files have the same columns
            if expected_columns is None:
                expected_columns = current_columns

            elif current_columns != expected_columns:
                missing_columns = [
                    col for col in expected_columns
                    if col not in current_columns
                ]

                extra_columns = [
                    col for col in current_columns
                    if col not in expected_columns
                ]

                raise ValueError(
                    f"Column mismatch in {input_file}\n"
                    f"Missing columns: {missing_columns}\n"
                    f"Extra columns: {extra_columns}"
                )

            file_rows = 0

            for chunk in pd.read_csv(
                input_file,
                chunksize=chunksize,
                # low_memory=False,
            ):
                chunk.to_csv(
                    output_handle,
                    index=False,
                    header=first_chunk,
                )

                first_chunk = False

                file_rows += len(chunk)
                total_rows += len(chunk)

            total_files += 1

            print(
                f"Completed: {input_file} "
                f"({file_rows:,} rows)",
                flush=True,
            )

    if total_files == 0:
        raise FileNotFoundError(
            "No monthly patient datasets were found."
        )

    print(
        f"Combined {total_files} monthly files.",
        flush=True,
    )

    print(
        f"Total rows written: {total_rows:,}",
        flush=True,
    )

    print(
        f"Saved: {output_file}",
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output",
        default="output/dataset_patients_combined.csv.gz",
        help="Output file path",
    )

    parser.add_argument(
        "--chunksize",
        type=int,
        default=100_000,
        help="Number of rows to process at one time",
    )

    args = parser.parse_args()

    combine_monthly_datasets(
        output_file=args.output,
        chunksize=args.chunksize,
    )

# import pandas as pd
# from pathlib import Path
# import config
# import argparse

# # utilisation: python analysis/project_setup/preprocess_combine_gz.py

# start_dates = config.month_range(config.start, config.end)
# # start_dates = ["2024-02-01", "2024-03-01"]

# dfs = []

# for d in start_dates:
#     file = Path(f"output/dataset_patients_{d}.csv.gz")

#     if file.exists():
#         df = pd.read_csv(file)
#         dfs.append(df)

# combined = pd.concat(dfs, ignore_index=True)

# parser = argparse.ArgumentParser()
# parser.add_argument(
#     "--output",
#     default="output/dataset_patients_combined.csv.gz",
#     help="Output file path"
# )

# args = parser.parse_args()
# combined.to_csv(args.output, index=False)
