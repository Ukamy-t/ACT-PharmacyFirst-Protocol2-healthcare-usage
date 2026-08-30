"""
This script validates and summarises the combined patient-level Pharmacy First dataset.

It:
- checks the compressed file size of the combined input dataset;
- reads the dataset in chunks to reduce memory usage;
- reads only the month and PF consultation variables required for the analysis;
- checks that all required variables are present;
- validates the start_date variable and identifies any missing or invalid dates;
- reports the months included in the combined dataset;
- validates consultation count variables for missing, negative, and non-integer values;
- calculates the min, max, and overall total for each consultation variable;
- calculates monthly consultation totals for each PF clinical pathway;
- saves the final monthly summary as pf_consultations_by_month.csv.
"""

import os
import pandas as pd


# =============================================================================
# Configuration
# =============================================================================

INPUT_FILE = "./output/dataset_patients_combined.csv.gz"
OUTPUT_FILE = "./output/pf_consultations_by_month.csv"
MONTH_COLUMN = "start_date"
CHUNKSIZE = 100_000

# CONSULTATION_COLUMNS = [
#     "numerator_pf_consultation_uti",
#     "numerator_pf_consultation_sinusitis",
#     "numerator_pf_consultation_insectbite",
#     "numerator_pf_consultation_otitismedia",
#     "numerator_pf_consultation_sorethroat",
#     "numerator_pf_consultation_shingles",
#     "numerator_pf_consultation_impetigo",
# ]

CONSULTATION_COLUMNS = [
    "num_pf_cons_uti",
    "num_pf_cons_sinusitis",
    "num_pf_cons_ibite",
    "num_pf_cons_otitismedia",
    "num_pf_cons_sorethroat",
    "num_pf_cons_shingles",
    "num_pf_cons_impetigo",
]

# =============================================================================
# Check input file and report file size
# =============================================================================

print(f"Current working directory: {os.getcwd()}")
print(f"Reading dataset: {INPUT_FILE}")

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

file_size_bytes = os.path.getsize(INPUT_FILE)

print("\nInput file size")
print("---------------")
print(f"Compressed file size: {file_size_bytes / 1024**2:,.2f} MB")
print(f"Compressed file size: {file_size_bytes / 1024**3:,.2f} GB")


# =============================================================================
# Read header and check required columns
# =============================================================================

header = pd.read_csv(INPUT_FILE, nrows=0)
all_columns = header.columns.tolist()

print(f"\nNumber of columns in full dataset: {len(all_columns):,}")

required_columns = [MONTH_COLUMN, *CONSULTATION_COLUMNS]

missing_columns = [
    column for column in required_columns
    if column not in all_columns
]

if missing_columns:
    raise ValueError(
        "The following required columns are missing:\n"
        + "\n".join(f"- {column}" for column in missing_columns)
    )

print("All required columns are present.")


# =============================================================================
# Initialise containers
# =============================================================================

total_rows = 0
invalid_start_dates = 0
months_found = set()

monthly_consultation_totals = {
    column: {} for column in CONSULTATION_COLUMNS
}

validation_results = {
    column: {
        "missing_values": 0,
        "negative_values": 0,
        "non_integer_values": 0,
        "minimum": None,
        "maximum": None,
        "total": 0,
    }
    for column in CONSULTATION_COLUMNS
}


# =============================================================================
# Read and process dataset in chunks
# =============================================================================

print("\nStarting chunk-based processing")

for chunk_number, chunk in enumerate(
    pd.read_csv(
        INPUT_FILE,
        usecols=required_columns,
        chunksize=CHUNKSIZE,
    ),
    start=1,
):
    print(f"Processing chunk {chunk_number}: {len(chunk):,} rows", flush=True)

    total_rows += len(chunk)

    chunk[MONTH_COLUMN] = pd.to_datetime(
        chunk[MONTH_COLUMN],
        errors="coerce",
    )

    invalid_start_dates += chunk[MONTH_COLUMN].isna().sum()

    valid_chunk = chunk.loc[
        chunk[MONTH_COLUMN].notna()
    ].copy()

    months_found.update(
        valid_chunk[MONTH_COLUMN].drop_duplicates()
    )

    # Validate consultation variables
    for column in CONSULTATION_COLUMNS:
        values = pd.to_numeric(
            valid_chunk[column],
            errors="coerce",
        )

        valid_chunk[column] = values

        validation_results[column]["missing_values"] += int(values.isna().sum())
        validation_results[column]["negative_values"] += int((values < 0).sum())
        validation_results[column]["non_integer_values"] += int(
            (values.notna() & (values % 1 != 0)).sum()
        )
        validation_results[column]["total"] += values.sum()

        chunk_min = values.min()
        chunk_max = values.max()

        if pd.notna(chunk_min):
            current_min = validation_results[column]["minimum"]
            if current_min is None or chunk_min < current_min:
                validation_results[column]["minimum"] = chunk_min

        if pd.notna(chunk_max):
            current_max = validation_results[column]["maximum"]
            if current_max is None or chunk_max > current_max:
                validation_results[column]["maximum"] = chunk_max

    # Calculate consultation totals for this chunk
    chunk_totals = (
        valid_chunk
        .groupby(MONTH_COLUMN)[CONSULTATION_COLUMNS]
        .sum(min_count=1)
    )

    # Add chunk totals to overall monthly totals
    for month, row in chunk_totals.iterrows():
        for column in CONSULTATION_COLUMNS:
            if pd.notna(row[column]):
                monthly_consultation_totals[column][month] = (
                    monthly_consultation_totals[column].get(month, 0)
                    + row[column]
                )


# =============================================================================
# Check processing results
# =============================================================================

print("\nDataset dimensions")
print("------------------")
print(f"Number of rows processed: {total_rows:,}")
print(f"Number of columns read for analysis: {len(required_columns):,}")

if invalid_start_dates > 0:
    raise ValueError(
        f"{invalid_start_dates:,} rows have a missing or invalid "
        f"{MONTH_COLUMN} value."
    )

sorted_months = sorted(months_found)

print("\nMonths included in the combined dataset")
print("---------------------------------------")

for month in sorted_months:
    print(month.strftime("%Y-%m-%d"))


# =============================================================================
# Consultation variable validation
# =============================================================================

validation_table = pd.DataFrame([
    {
        "variable": column,
        **validation_results[column],
    }
    for column in CONSULTATION_COLUMNS
])

print("\nConsultation variable validation")
print("--------------------------------")
print(validation_table.to_string(index=False))


# =============================================================================
# Create monthly consultation summary
# =============================================================================

monthly_summary = pd.DataFrame([
    {
        MONTH_COLUMN: month,
        **{
            column: monthly_consultation_totals[column].get(month, 0)
            for column in CONSULTATION_COLUMNS
        },
    }
    for month in sorted_months
])

monthly_summary = monthly_summary.sort_values(MONTH_COLUMN)

monthly_summary[MONTH_COLUMN] = (
    monthly_summary[MONTH_COLUMN]
    .dt.strftime("%Y-%m")
)


# =============================================================================
# Display and save results
# =============================================================================

print("\nMonthly Pharmacy First consultation totals")
print("------------------------------------------")
print(monthly_summary.to_string(index=False))

monthly_summary.to_csv(
    OUTPUT_FILE,
    index=False,
)

print(f"\nMonthly summary saved to: {OUTPUT_FILE}")