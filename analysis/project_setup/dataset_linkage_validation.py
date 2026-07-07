import pandas as pd

patient_file = "output/dataset_patients_combined.csv.gz"
practice_file = "output/dataset_practices.csv.gz"

patients = pd.read_csv(patient_file)
practices = pd.read_csv(practice_file)


# Standardise month variable
patients["month"] = pd.to_datetime(
    patients["index_date"]
)

practices["month"] = pd.to_datetime(
    practices["interval_end"]
)


# ------------------------------------------------------------------
# Patient-level data checks
# ------------------------------------------------------------------

print("\n")
print("=" * 80)
print("PATIENT-LEVEL DATA")
print("=" * 80)


print("\nDataset shape")
print(f"Rows: {len(patients):,}")
print(f"Columns: {len(patients.columns):,}")


print("\nColumns")
for column in patients.columns:
    print(column)


print("\nData types")
print(patients.dtypes)


print("\nMissing data")
patient_missing = (
    patients
    .isna()
    .sum()
    .to_frame("n_missing")
)

patient_missing["percent_missing"] = (
    patient_missing["n_missing"]
    / len(patients)
    * 100
)

patient_missing = (
    patient_missing
    .sort_values(
        "percent_missing",
        ascending=False,
    )
)

print(patient_missing)


print("\nNumber of months")
print(patients["month"].nunique())


print("\nMonth range")
print(
    patients["month"].min(),
    "to",
    patients["month"].max(),
)


print("\nNumber of unique patients")
print(
    patients["patient_id"].nunique()
)


print("\nRows per month")
print(
    patients
    .groupby("month")
    .size()
)


# ------------------------------------------------------------------
# Check patient-month uniqueness
# ------------------------------------------------------------------

patient_month_duplicates = patients.duplicated(
    subset=[
        "patient_id",
        "month",
    ],
    keep=False,
)


print("\nDuplicated patient-month rows")
print(
    patient_month_duplicates.sum()
)


if patient_month_duplicates.any():
    print(
        patients.loc[
            patient_month_duplicates,
            [
                "patient_id",
                "month",
                "practice",
            ],
        ]
        .sort_values(
            [
                "patient_id",
                "month",
            ]
        )
        .head(20)
    )


# ------------------------------------------------------------------
# Practice-level data checks
# ------------------------------------------------------------------

print("\n")
print("=" * 80)
print("PRACTICE-LEVEL DATA")
print("=" * 80)


print("\nDataset shape")
print(f"Rows: {len(practices):,}")
print(f"Columns: {len(practices.columns):,}")


print("\nColumns")
for column in practices.columns:
    print(column)


print("\nData types")
print(practices.dtypes)


print("\nMissing data")
practice_missing = (
    practices
    .isna()
    .sum()
    .to_frame("n_missing")
)

practice_missing["percent_missing"] = (
    practice_missing["n_missing"]
    / len(practices)
    * 100
)

practice_missing = (
    practice_missing
    .sort_values(
        "percent_missing",
        ascending=False,
    )
)

print(practice_missing)


print("\nNumber of months")
print(
    practices["month"].nunique()
)


print("\nMonth range")
print(
    practices["month"].min(),
    "to",
    practices["month"].max(),
)


print("\nNumber of unique practices")
print(
    practices["practice"].nunique()
)


print("\nPractices per month")
print(
    practices
    .groupby("month")["practice"]
    .nunique()
)


# ------------------------------------------------------------------
# Check practice-month uniqueness
# ------------------------------------------------------------------

practice_month_duplicates = practices.duplicated(
    subset=[
        "practice",
        "month",
    ],
    keep=False,
)


print("\nDuplicated practice-month rows")
print(
    practice_month_duplicates.sum()
)


if practice_month_duplicates.any():
    print(
        practices.loc[
            practice_month_duplicates
        ]
        .sort_values(
            [
                "practice",
                "month",
            ]
        )
        .head(20)
    )


# ------------------------------------------------------------------
# Practice linkage checks
# ------------------------------------------------------------------

print("\n")
print("=" * 80)
print("PATIENT-PRACTICE LINKAGE")
print("=" * 80)


linkage = patients.merge(
    practices[
        [
            "practice",
            "month",
        ]
    ],
    on=[
        "practice",
        "month",
    ],
    how="left",
    indicator=True,
    validate="many_to_one",
)


print("\nMerge status")
print(
    linkage["_merge"]
    .value_counts(dropna=False)
)


print("\nMerge status (%)")
print(
    linkage["_merge"]
    .value_counts(
        normalize=True,
        dropna=False,
    )
    .mul(100)
)


# ------------------------------------------------------------------
# Unmatched patient rows
# ------------------------------------------------------------------

unmatched_patients = linkage.loc[
    linkage["_merge"] == "left_only"
].copy()


print("\nPatient rows not matched to practice-level data")
print(
    len(unmatched_patients)
)


print("\nUnique unmatched patients")
print(
    unmatched_patients["patient_id"].nunique()
)


print("\nUnmatched rows by month")
print(
    unmatched_patients
    .groupby("month")
    .size()
)


print("\nUnmatched rows by practice")
print(
    unmatched_patients
    .groupby("practice")
    .size()
    .sort_values(ascending=False)
    .head(20)
)


# ------------------------------------------------------------------
# Missing practice ID in patient data
# ------------------------------------------------------------------

missing_patient_practice = (
    patients["practice"]
    .isna()
)


print("\nPatient rows with missing practice ID")
print(
    missing_patient_practice.sum()
)


print("\nPercentage of patient rows with missing practice ID")
print(
    missing_patient_practice.mean() * 100
)