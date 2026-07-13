import pandas as pd

INPUT_FILE = "output/patient_measures_insectbites.csv"
OUTPUT_FILE = "output/patient_measures_insectbites_summary.csv"

measures = pd.read_csv(INPUT_FILE)

# Keep patient and consultation count measures
measures = measures[
    measures["measure"].str.startswith(
        ("n_patients_", "n_consultations_")
    )
].copy()

# Identify metric type
measures["metric"] = measures["measure"].str.extract(
    r"^(n_patients|n_consultations)_"
)[0]

# Extract codelist / definition name
measures["definition"] = measures["measure"].str.replace(
    r"^(n_patients|n_consultations)_",
    "",
    regex=True,
)

# Reshape into one row per interval and definition
summary = (
    measures.pivot_table(
        index=[
            "interval_start",
            "interval_end",
            "definition",
        ],
        columns="metric",
        values="numerator",
        aggfunc="first",
    )
    .reset_index()
    .rename(
        columns={
            "n_patients": "number_of_patients",
            "n_consultations": "number_of_consultations",
        }
    )
)

# Set definition display order
definition_order = [
    "insectbite",
    "insectbite_strict",
    "insectbite_all",
    "cellulitis_only",
    "insectbite_strict_or_all",
    "insectbite_all_plus_cellulitis",
    "insectbite_strict_or_all_plus_cellulitis"
]

summary["definition"] = pd.Categorical(
    summary["definition"],
    categories=definition_order,
    ordered=True,
)

summary = summary.sort_values(
    ["interval_start", "definition"]
)

# Save summary table
summary.to_csv(
    OUTPUT_FILE,
    index=False,
)
