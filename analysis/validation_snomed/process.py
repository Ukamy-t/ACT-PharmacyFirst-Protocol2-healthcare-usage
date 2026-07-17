import pandas as pd

"""
This script processes the patient-level SNOMED code count datasets generated for each PF condition.

For each PF condition:
- read the patient-level dataset;
- reshape the data from wide to long format;
- aggregate consultation counts to SNOMED-code level;
- merge with the corresponding SNOMED term lookup from the original codelist CSV;
- produce summary tables of the number of unique GP consultations in which each SNOMED code appeared;
- generates visualisations showing the most frequently recorded SNOMED codes for each PF condition.
"""

conditions = [
    "uti",
    "sinusitis",
    "insectbite",
    "otitismedia",
    "sorethroat",
    "shingles",
    "impetigo",
]

gp_snomed_codelist_files = {
    "uti": "codelists/pharmacy-first-project-urinary-tract-infection-and-related-conditions-for-pharamcy-first-clone.csv",
    "sinusitis": "codelists/pharmacy-first-project-sinusitis-related-conditions-administration-codes-for-pharmacy-first.csv",
    "insectbite": "codelists/pharmacy-first-project-insect-bites-and-related-conditions-administration-codes-for-pharmacy-first.csv",
    "otitismedia": "codelists/pharmacy-first-project-otitis-media-and-related-conditions.csv",
    "sorethroat": "codelists/pharmacy-first-project-Sore-throat-and-related-conditions.csv",
    "shingles": "codelists/pharmacy-first-project-shingles-and-related-conditions-for-pharmacy-first.csv",
    "impetigo": "codelists/pharmacy-first-project-impetigo-related-conditions-administration-codes-for-pharmacy-first.csv",
}

for condition in conditions:
    print("Starting for condition:", condition, "...", flush=True)

    input_file = f"output/dataset_patients_snomed_{condition}.csv.gz"

    header = pd.read_csv(input_file, nrows=0)
    count_cols = [
        col for col in header.columns
        if col.startswith("count_")
    ]
    print(f"{condition}: {len(count_cols)} count columns", flush=True)

    # -------------------------------------------------
    # Sum count columns in chunks
    # -------------------------------------------------
    total_counts = pd.Series(0, index=count_cols, dtype="int64")

    for chunk in pd.read_csv(
        input_file,
        usecols=count_cols,
        chunksize=100_000,
        dtype={col: "int64" for col in count_cols},
        # low_memory=False,
    ):
        total_counts = total_counts.add(chunk.sum(), fill_value=0).astype("int64")

    summary = total_counts.reset_index()
    summary.columns = ["snomed_code", "consultation_count"]

    summary["snomed_code"] = (
        summary["snomed_code"]
        .str.replace("count_", "", regex=False)
        .astype(str)
    )

    # Read condition-specific codelist lookup
    lookup = pd.read_csv(gp_snomed_codelist_files[condition],dtype={"code": str},)
    lookup = lookup.rename(columns={"code": "snomed_code"})

    # Keep only relevant lookup columns
    if "term" in lookup.columns:
        lookup = lookup[["snomed_code", "term"]].drop_duplicates()
    else:
        lookup["term"] = ""
        lookup = lookup[["snomed_code", "term"]].drop_duplicates()
    
    summary = summary.merge(
        lookup,
        on="snomed_code",
        how="left",
    )

    # Add condition column
    summary.insert(0, "condition", condition)

    summary = summary[
        ["condition", "snomed_code", "term", "consultation_count"]
    ]

    summary = summary.sort_values(
        "consultation_count",
        ascending=False,
    )

    output_file = f"output/snomed_count_summary_{condition}.csv"
    summary.to_csv(output_file, index=False)
    print(f"Saved: {output_file}", flush=True)
