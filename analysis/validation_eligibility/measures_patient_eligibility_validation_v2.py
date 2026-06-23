from ehrql import case, create_measures, months, when
from analysis.validation_eligibility.dataset_definition_patients_measures_v2 import dataset

measures = create_measures()
measures.configure_disclosure_control(enabled=False)
measures.define_defaults(
    intervals=months(1).starting_on("2025-10-01"),
    # intervals=months(1).starting_on("2024-02-01")
)

measure_base_population = (
    dataset.alive
    & dataset.registered_start
    & dataset.registered_index
    & (dataset.age <= 120)
)

pf_eligible_population = (
    dataset.include_patient_overall_eligible
    & measure_base_population
)

pf_user_population = (
    (dataset.pf_consultation_general > 0)
    & measure_base_population
)

measures.define_measure(
    name="debug_population_by_sex",
    numerator=pf_user_population,
    denominator=measure_base_population,
    group_by={"sex": dataset.sex},
)

measures.define_measure(
    name="debug_base_population_as_numerator",
    numerator=measure_base_population,
    denominator=measure_base_population,
)

measures.define_measure(
    name="debug_age_valid_as_numerator",
    numerator=dataset.age <= 120,
    denominator=measure_base_population,
)

'''
Impetigo:
    - Inclusion: age >= 1
    - Exclusion:
        - Bullous impetigo
        - Recurrent impetigo
        - Pregnant female under 16s

Checks:
- Bullous impetigo and recurrent impetigo should both be rare in the base population.
- The overlap between bullous and recurrent impetigo should also be very small.
- include_patient_impetigo should mainly reflect the majority of patients.
- Among patients with at least one PF impetigo consultation who were classified as not eligible, check the exclusion reasons.
'''
measures.define_measure(
    name="bullous_impetigo_among_base",
    numerator=dataset.bullous_impetigo_this_month,
    denominator=measure_base_population,
)

measures.define_measure(
    name="recurrent_impetigo_among_base",
    numerator=dataset.recurrent_impetigo_this_year,
    denominator=measure_base_population,
)

measures.define_measure(
    name="bullous_and_recurrent_impetigo_among_base",
    numerator=dataset.bullous_impetigo_this_month & dataset.recurrent_impetigo_this_year,
    denominator=measure_base_population,
)

age_band_impetigo = case(
    when(dataset.age.is_null()).then("Missing"),
    when(dataset.age < 1).then("<1"),
    when(dataset.age < 16).then("1-15"),
    when(dataset.age < 17).then("16"),
    when(dataset.age <= 64).then("17-64"),
    when(dataset.age > 64).then("65+"),
    # otherwise="65+",
)
# debug_age_band_simple = case(
#     when(dataset.age.is_null()).then("Missing"),
#     when(dataset.age < 1).then("<1"),
#     otherwise="1+",
# )
measures.define_measure(
    name="impetigo_eligible_among_base",
    numerator=dataset.include_patient_impetigo,
    denominator=measure_base_population,
    # group_by={"debug_age_band_simple": debug_age_band_simple},
    group_by={"age_band_impetigo": age_band_impetigo},
)

impetigo_excluded_population = (
    measure_base_population
    & ~dataset.include_patient_impetigo
)

measures.define_measure(
    name="impetigo_excluded_among_base_by_age_band",
    numerator=~dataset.include_patient_impetigo,
    denominator=measure_base_population,
    group_by={"age_band_impetigo": age_band_impetigo},
)

measures.define_measure(
    name="impetigo_excluded_among_base_due_to_bullous",
    numerator=dataset.bullous_impetigo_this_month,
    denominator=impetigo_excluded_population,
)

measures.define_measure(
    name="impetigo_excluded_among_base_due_to_recurrent",
    numerator=dataset.recurrent_impetigo_this_year,
    denominator=impetigo_excluded_population,
)

measures.define_measure(
    name="impetigo_excluded_among_base_due_to_pregnant_female_under16",
    numerator=(
        dataset.pregnant_this_month
        & (dataset.sex == "female")
        & (dataset.age < 16)
    ),
    denominator=impetigo_excluded_population,
)

impetigo_pf_user_population = (
    (dataset.numerator_pf_consultation_impetigo > 0)
    & measure_base_population
)

impetigo_pf_user_not_eligible_population = (
    impetigo_pf_user_population
    & ~dataset.include_patient_impetigo
)

measures.define_measure(
    name="impetigo_pf_users_not_eligible",
    numerator=~dataset.include_patient_impetigo,
    denominator=impetigo_pf_user_population,
)

measures.define_measure(
    name="impetigo_pf_users_not_eligible_by_age_band",
    numerator=~dataset.include_patient_impetigo,
    denominator=impetigo_pf_user_population,
    group_by={"age_band_impetigo": age_band_impetigo},
)

measures.define_measure(
    name="impetigo_pf_users_not_eligible_due_to_bullous",
    numerator=dataset.bullous_impetigo_this_month,
    denominator=impetigo_pf_user_not_eligible_population,
)

measures.define_measure(
    name="impetigo_pf_users_not_eligible_due_to_recurrent",
    numerator=dataset.recurrent_impetigo_this_year,
    denominator=impetigo_pf_user_not_eligible_population,
)

measures.define_measure(
    name="impetigo_pf_users_not_eligible_due_to_pregnant_female_under16",
    numerator=(
        dataset.pregnant_this_month
        & (dataset.sex == "female")
        & (dataset.age < 16)
    ),
    denominator=impetigo_pf_user_not_eligible_population,
)

measures.define_measure(
    name="impetigo_pf_users_not_eligible_by_sex_age_pregnancy",
    numerator=~dataset.include_patient_impetigo,
    denominator=impetigo_pf_user_population,
    group_by={
        "sex": dataset.sex,
        "age_band_impetigo": age_band_impetigo,
        "pregnant": dataset.pregnant,
    },
)


'''
UTI:
    - Inclusion: women aged 16 to 64 years
    - Exclusion:
        - Pregnant female
        - Urinary catheter
        - Recurrent UTI

Checks:
- catheter_status, recurrent_uti_6m, recurrent_uti_12m, and recurrent_uti should be relatively uncommon in the base population.
- recurrent_uti should be greater than or equal to both recurrent_uti_6m and recurrent_uti_12m.
- include_patient_uuti should only appear among females aged 16-64.
- Among base population patients excluded from UTI eligibility, check the exclusion reasons.
- Among patients with at least one PF UTI consultation who were classified as not eligible, check the exclusion reasons.
'''
age_band_uti = case(
    when(dataset.age.is_null()).then("Missing"),
    when(dataset.age < 1).then("<1"),  # not eligible
    when((dataset.age >= 1) & (dataset.age < 15)).then("1-14"),  # not eligible
    when((dataset.age >= 15) & (dataset.age < 16)).then("15"),  # not eligible - lower age boundary
    when((dataset.age >= 16) & (dataset.age <= 64)).then("16-64"),  # eligible age range
    when((dataset.age >= 65) & (dataset.age < 66)).then("65"),  # not eligible - upper age boundary
    when(dataset.age > 65).then("66+"),  # not eligible
)

measures.define_measure(
    name="catheter_status_among_base",
    numerator=dataset.catheter_status,
    denominator=measure_base_population,
)

measures.define_measure(
    name="recurrent_uti_6m_among_base",
    numerator=dataset.recurrent_uti_6m,
    denominator=measure_base_population,
)

measures.define_measure(
    name="recurrent_uti_12m_among_base",
    numerator=dataset.recurrent_uti_12m,
    denominator=measure_base_population,
)

measures.define_measure(
    name="recurrent_uti_among_base",
    numerator=dataset.recurrent_uti,
    denominator=measure_base_population,
)

measures.define_measure(
    name="uti_eligible_among_base",
    numerator=dataset.include_patient_uuti,
    denominator=measure_base_population,
    group_by={
        "sex": dataset.sex,
        "age_band_uti": age_band_uti,
    },
)

uti_excluded_population = (
    measure_base_population
    & ~dataset.include_patient_uuti
)

measures.define_measure(
    name="uti_excluded_among_base_by_sex_age_band",
    numerator=~dataset.include_patient_uuti,
    denominator=measure_base_population,
    group_by={
        "sex": dataset.sex,
        "age_band_uti": age_band_uti,
    },
)

measures.define_measure(
    name="uti_excluded_among_base_due_to_age_sex",
    numerator=~(
        (dataset.sex == "female")
        & (dataset.age >= 16)
        & (dataset.age <= 64)
    ),
    denominator=uti_excluded_population,
)

measures.define_measure(
    name="uti_excluded_among_base_due_to_pregnant_female",
    numerator=(
        dataset.pregnant_this_month
        & (dataset.sex == "female")
    ),
    denominator=uti_excluded_population,
)

measures.define_measure(
    name="uti_excluded_among_base_due_to_catheter",
    numerator=dataset.catheter_status,
    denominator=uti_excluded_population,
)

measures.define_measure(
    name="uti_excluded_among_base_due_to_recurrent_uti",
    numerator=dataset.recurrent_uti,
    denominator=uti_excluded_population,
)

uti_pf_user_population = (
    (dataset.numerator_pf_consultation_uti > 0)
    & measure_base_population
)

uti_pf_user_not_eligible_population = (
    uti_pf_user_population
    & ~dataset.include_patient_uuti
)

measures.define_measure(
    name="uti_pf_users_not_eligible",
    numerator=~dataset.include_patient_uuti,
    denominator=uti_pf_user_population,
)

measures.define_measure(
    name="uti_pf_users_not_eligible_by_sex_age_band",
    numerator=~dataset.include_patient_uuti,
    denominator=uti_pf_user_population,
    group_by={
        "sex": dataset.sex,
        "age_band_uti": age_band_uti,
    },
)

measures.define_measure(
    name="uti_pf_users_not_eligible_due_to_age_sex",
    numerator=~(
        (dataset.sex == "female")
        & (dataset.age >= 16)
        & (dataset.age <= 64)
    ),
    denominator=uti_pf_user_not_eligible_population,
)

measures.define_measure(
    name="uti_pf_users_not_eligible_due_to_pregnant_female",
    numerator=(
        dataset.pregnant_this_month
        & (dataset.sex == "female")
    ),
    denominator=uti_pf_user_not_eligible_population,
)

measures.define_measure(
    name="uti_pf_users_not_eligible_due_to_catheter",
    numerator=dataset.catheter_status,
    denominator=uti_pf_user_not_eligible_population,
)

measures.define_measure(
    name="uti_pf_users_not_eligible_due_to_recurrent_uti",
    numerator=dataset.recurrent_uti,
    denominator=uti_pf_user_not_eligible_population,
)

measures.define_measure(
    name="uti_pf_users_not_eligible_by_sex_age_pregnancy",
    numerator=~dataset.include_patient_uuti,
    denominator=uti_pf_user_population,
    group_by={
        "sex": dataset.sex,
        "age_band_uti": age_band_uti,
        "pregnant": dataset.pregnant,
    },
)