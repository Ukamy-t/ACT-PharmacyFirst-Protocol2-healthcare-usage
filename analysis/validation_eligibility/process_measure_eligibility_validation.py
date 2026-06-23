import pandas as pd


input_file_v2 = "output/patient_measures_eligibility_validation_v2.csv"
input_file_v3 = "output/patient_measures_eligibility_validation_v3.csv"

output_file_v2 = "output/patient_measures_eligibility_validation_ordered_v2.csv"
output_file_v3 = "output/patient_measures_eligibility_validation_ordered_v3.csv"


measure_order = [
    # debug
    "debug_population_by_sex",
    "debug_base_population_as_numerator",
    "debug_age_valid_as_numerator",

    # Impetigo
    "bullous_impetigo_among_base",
    "recurrent_impetigo_among_base",
    "bullous_and_recurrent_impetigo_among_base",
    "impetigo_eligible_among_base",
    "impetigo_excluded_among_base_by_age_band",
    "impetigo_excluded_among_base_due_to_bullous",
    "impetigo_excluded_among_base_due_to_recurrent",
    "impetigo_excluded_among_base_due_to_pregnant_female_under16",
    "impetigo_pf_users_not_eligible",
    "impetigo_pf_users_not_eligible_by_age_band",
    "impetigo_pf_users_not_eligible_due_to_bullous",
    "impetigo_pf_users_not_eligible_due_to_recurrent",
    "impetigo_pf_users_not_eligible_due_to_pregnant_female_under16",
    "impetigo_pf_users_not_eligible_by_sex_age_pregnancy",

    # UTI
    "catheter_status_among_base",
    "recurrent_uti_6m_among_base",
    "recurrent_uti_12m_among_base",
    "recurrent_uti_among_base",
    "uti_eligible_among_base",
    "uti_excluded_among_base_by_sex_age_band",
    "uti_excluded_among_base_due_to_age_sex",
    "uti_excluded_among_base_due_to_pregnant_female",
    "uti_excluded_among_base_due_to_catheter",
    "uti_excluded_among_base_due_to_recurrent_uti",
    "uti_pf_users_not_eligible",
    "uti_pf_users_not_eligible_by_sex_age_band",
    "uti_pf_users_not_eligible_due_to_age_sex",
    "uti_pf_users_not_eligible_due_to_pregnant_female",
    "uti_pf_users_not_eligible_due_to_catheter",
    "uti_pf_users_not_eligible_due_to_recurrent_uti",
    "uti_pf_users_not_eligible_by_sex_age_pregnancy",

    # Overall eligible
    "pf_overall_eligible_among_base",
    "pf_overall_user_not_eligible",
]


def process_measure_file(input_file, output_file, version):
    df = pd.read_csv(input_file)

    measure_rank = {measure: i for i, measure in enumerate(measure_order)}

    df["measure_order"] = (
        df["measure"]
        .map(measure_rank)
        .fillna(999)
        .astype(int)
    )

    # Combine condition-specific age-band columns into one display column.
    age_band_cols = [
        "age_band_impetigo",
        "age_band_uti",
    ]

    existing_age_band_cols = [col for col in age_band_cols if col in df.columns]

    if existing_age_band_cols:
        df["age_band"] = (
            df[existing_age_band_cols]
            .bfill(axis=1)
            .iloc[:, 0]
        )
        df = df.drop(columns=existing_age_band_cols)

    # Add version column so the outputs are traceable.
    df["version"] = version

    sort_cols = ["measure_order", "measure", "interval_start"]

    for col in ["sex", "age_band", "pregnant"]:
        if col in df.columns:
            sort_cols.append(col)

    df = df.sort_values(sort_cols).drop(columns=["measure_order"])

    # Optional: put commonly reviewed columns near the front
    front_cols = [
        "version",
        "measure",
        "interval_start",
        "interval_end",
        "pregnant",
        "sex",
        "age_band",
        "numerator",
        "denominator",
        "ratio",
    ]

    front_cols = [col for col in front_cols if col in df.columns]
    other_cols = [col for col in df.columns if col not in front_cols]
    df = df[front_cols + other_cols]

    df.to_csv(output_file, index=False)

    unknown_measures = sorted(set(df["measure"]) - set(measure_order))

    print(f"Saved ordered measures for {version} to {output_file}")

    if unknown_measures:
        print(
            f"Warning for {version}: the following measures were not included "
            "in measure_order and were placed at the end:"
        )
        for measure in unknown_measures:
            print(f"- {measure}")


process_measure_file(
    input_file=input_file_v2,
    output_file=output_file_v2,
    version="v2",
)

process_measure_file(
    input_file=input_file_v3,
    output_file=output_file_v3,
    version="v3",
)