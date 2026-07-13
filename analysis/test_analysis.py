import os

import pandas as pd


# =============================================================================
# Configuration
# =============================================================================

INPUT_FILE = "./output/dataset_patients_combined.csv.gz"
OUTPUT_FILE = "./output/pf_consultations_by_month.csv"

MONTH_COLUMN = "start_date"

CONSULTATION_COLUMNS = [
    "numerator_pf_consultation_uti",
    "numerator_pf_consultation_sinusitis",
    "numerator_pf_consultation_insectbite",
    "numerator_pf_consultation_otitismedia",
    "numerator_pf_consultation_sorethroat",
    "numerator_pf_consultation_shingles",
    "numerator_pf_consultation_impetigo",
]


# =============================================================================
# Read combined monthly patient dataset
# =============================================================================

cwd = os.getcwd()
print(f"Current working directory: {cwd}")
print(f"Reading dataset: {INPUT_FILE}")

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

print("\nDataset dimensions")
print("------------------")
print(f"Number of rows: {len(df):,}")
print(f"Number of columns: {len(df.columns):,}")

print("\nFirst five rows")
print("---------------")
print(df.head())

print("\nColumns")
print("-------")
for column in df.columns:
    print(column)


# =============================================================================
# Check required columns
# =============================================================================

required_columns = [
    "patient_id",
    MONTH_COLUMN,
    *CONSULTATION_COLUMNS,
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "The following required columns are missing:\n"
        + "\n".join(f"- {column}" for column in missing_columns)
    )

print("\nAll required columns are present.")


# =============================================================================
# Prepare start_date
# =============================================================================

df[MONTH_COLUMN] = pd.to_datetime(
    df[MONTH_COLUMN],
    errors="coerce",
)

invalid_start_dates = df[MONTH_COLUMN].isna().sum()

if invalid_start_dates > 0:
    raise ValueError(
        f"{invalid_start_dates:,} rows have a missing or invalid "
        f"{MONTH_COLUMN} value."
    )

print("\nMonths included in the combined dataset")
print("---------------------------------------")
print(
    df[MONTH_COLUMN]
    .drop_duplicates()
    .sort_values()
    .dt.strftime("%Y-%m-%d")
    .to_string(index=False)
)


# =============================================================================
# Check patient-month rows
# =============================================================================

duplicate_patient_month = df.duplicated(
    subset=["patient_id", MONTH_COLUMN],
    keep=False,
)

number_of_duplicate_rows = duplicate_patient_month.sum()

print("\nDuplicate patient-month check")
print("-----------------------------")
print(
    "Number of rows belonging to duplicated patient-month combinations: "
    f"{number_of_duplicate_rows:,}"
)

if number_of_duplicate_rows > 0:
    duplicate_summary = (
        df.loc[
            duplicate_patient_month,
            ["patient_id", MONTH_COLUMN],
        ]
        .value_counts()
        .reset_index(name="number_of_rows")
        .sort_values(
            [MONTH_COLUMN, "number_of_rows"],
            ascending=[True, False],
        )
    )

    print("\nExample duplicate patient-month combinations")
    print("--------------------------------------------")
    print(duplicate_summary.head(20).to_string(index=False))


# =============================================================================
# Validate consultation variables
# =============================================================================

validation_results = []

for column in CONSULTATION_COLUMNS:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    )

    missing_count = df[column].isna().sum()
    negative_count = (df[column] < 0).sum()

    non_integer_count = (
        df[column].notna()
        & (df[column] % 1 != 0)
    ).sum()

    validation_results.append(
        {
            "variable": column,
            "missing_values": missing_count,
            "negative_values": negative_count,
            "non_integer_values": non_integer_count,
            "minimum": df[column].min(),
            "maximum": df[column].max(),
            "total": df[column].sum(),
        }
    )

validation_table = pd.DataFrame(validation_results)

print("\nConsultation variable validation")
print("--------------------------------")
print(validation_table.to_string(index=False))


# =============================================================================
# Dataset rows and unique patients in each month
# =============================================================================

monthly_population = (
    df.groupby(MONTH_COLUMN, as_index=False)
    .agg(
        number_of_rows=("patient_id", "size"),
        number_of_unique_patients=("patient_id", "nunique"),
    )
)


# =============================================================================
# Total number of consultations in each month
# =============================================================================

monthly_consultations = (
    df.groupby(
        MONTH_COLUMN,
        as_index=False,
    )[CONSULTATION_COLUMNS]
    .sum(min_count=1)
)


# Combine population and consultation summaries
monthly_summary = monthly_population.merge(
    monthly_consultations,
    on=MONTH_COLUMN,
    how="left",
)

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