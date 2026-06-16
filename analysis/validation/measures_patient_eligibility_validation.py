from ehrql import case, create_measures, months, when
from analysis.dataset_definition_patients_measures import dataset

measures = create_measures()
measures.configure_disclosure_control(enabled=False)
measures.define_defaults(
    intervals=months(1).starting_on("2025-10-01"),
    # intervals=years(2).starting_on("2024-02-01")
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


'''
Pregnancy-related: overall, by sex and age band

Checks:
- any records with sex == "unknown"?
- any pregnancy records among males?
- any pregnancy records among patients aged <=16 years?
'''
age_band_pregnancy_validation = case(
    when(dataset.age.is_null()).then("Missing"),
    when(dataset.age < 11).then("<11"),
    when((dataset.age >= 11) & (dataset.age < 16)).then("11-15"),
    when((dataset.age >= 16) & (dataset.age < 20)).then("16-19"),
    when((dataset.age >= 20) & (dataset.age <= 40)).then("20-40"),
    when((dataset.age >= 41) & (dataset.age <= 64)).then("41-64"),
    when(dataset.age > 64).then("65+"),
)

measures.define_measure(
    name="pregnancy_category_among_base",
    numerator=dataset.pregnant_this_month,
    denominator=measure_base_population,
    group_by={"pregnant": dataset.pregnant},
)

measures.define_measure(
    name="pregnant_this_month_among_base_by_sex_age_validation",
    numerator=dataset.pregnant_this_month,
    denominator=measure_base_population,
    group_by={
        "sex": dataset.sex,
        "age_band_pregnancy_validation": age_band_pregnancy_validation,
    },
)


'''
For each PF condition, this validation uses two complementary perspectives:

1. Among patients with a PF consultation for that condition, how many were classified as not eligible, and why?
2. Among base population patients excluded from that condition-specific eligibility, what exclusion criteria explain the exclusion?

Exclusion reasons may overlap, so their proportions do not need to sum to 100%.
'''


'''
Otitis media:
    - Inclusion: children aged 1 to 17 years old
    - Exclusion: none

Checks:
- Among patients with at least one PF otitis media consultation, what proportion were classified as not eligible?
- Break down apparent ineligibility by otitis-media-specific age band, particularly around the age boundaries.
'''
age_band_otitismedia = case(
    when(dataset.age.is_null()).then("Missing"),
    when(dataset.age < 1).then("<1"),  # not eligible - lower age boundary
    when((dataset.age >= 1) & (dataset.age < 18)).then("1-17"),  # eligible
    when((dataset.age >= 18) & (dataset.age < 19)).then("18"),  # not eligible - upper age boundary
    when((dataset.age >= 19) & (dataset.age <= 64)).then("19-64"),  # not eligible
    when(dataset.age > 64).then("65+"),  # not eligible
)

measures.define_measure(
    name="otitismedia_eligible_among_base",
    numerator=dataset.include_patient_otitis_media,
    denominator=measure_base_population,
    group_by={"age_band_otitismedia": age_band_otitismedia},
)

measures.define_measure(
    name="otitismedia_excluded_among_base_by_age_band",
    numerator=~dataset.include_patient_otitis_media,
    denominator=measure_base_population,
    group_by={"age_band_otitismedia": age_band_otitismedia},
)

otitismedia_pf_user_population = (
    (dataset.numerator_pf_consultation_otitismedia > 0)
    & measure_base_population
)

measures.define_measure(
    name="otitismedia_pf_users_not_eligible",
    numerator=~dataset.include_patient_otitis_media,
    denominator=otitismedia_pf_user_population,
)

measures.define_measure(
    name="otitismedia_pf_users_not_eligible_by_age_band",
    numerator=~dataset.include_patient_otitis_media,
    denominator=otitismedia_pf_user_population,
    group_by={"age_band_otitismedia": age_band_otitismedia},
)


'''
Sinusitis:
    - Inclusion: age >= 12
    - Exclusion: none

Checks:
- Among patients with at least one PF sinusitis consultation, what proportion were classified as not eligible?
- Break down apparent ineligibility by sinusitis-specific age band, particularly around the age boundary.
'''
age_band_sinusitis = case(
    when(dataset.age.is_null()).then("Missing"),
    when(dataset.age < 1).then("<1"),  # not eligible
    when((dataset.age >= 1) & (dataset.age < 11)).then("1-10"),  # not eligible
    when((dataset.age >= 11) & (dataset.age < 12)).then("11"),  # not eligible - age boundary
    when((dataset.age >= 12) & (dataset.age <= 64)).then("12-64"),  # eligible
    when(dataset.age > 64).then("65+"),  # eligible
)

measures.define_measure(
    name="sinusitis_eligible_among_base",
    numerator=dataset.include_patient_sinusitis,
    denominator=measure_base_population,
    group_by={"age_band_sinusitis": age_band_sinusitis},
)

measures.define_measure(
    name="sinusitis_excluded_among_base_by_age_band",
    numerator=~dataset.include_patient_sinusitis,
    denominator=measure_base_population,
    group_by={"age_band_sinusitis": age_band_sinusitis},
)

sinusitis_pf_user_population = (
    (dataset.numerator_pf_consultation_sinusitis > 0)
    & measure_base_population
)

measures.define_measure(
    name="sinusitis_pf_users_not_eligible",
    numerator=~dataset.include_patient_sinusitis,
    denominator=sinusitis_pf_user_population,
)

measures.define_measure(
    name="sinusitis_pf_users_not_eligible_by_age_band",
    numerator=~dataset.include_patient_sinusitis,
    denominator=sinusitis_pf_user_population,
    group_by={"age_band_sinusitis": age_band_sinusitis},
)


'''
Sore throat:
    - Inclusion: age >= 5
    - Exclusion: pregnant female under 16s

Checks:
- Among patients with at least one PF sore throat consultation, what proportion were classified as not eligible?
- Break down apparent ineligibility by age band and pregnancy-related exclusion.
'''
age_band_sorethroat = case(
    when(dataset.age.is_null()).then("Missing"),
    when(dataset.age < 1).then("<1"),  # not eligible
    when((dataset.age >= 1) & (dataset.age < 4)).then("1-3"),  # not eligible
    when((dataset.age >= 4) & (dataset.age < 5)).then("4"),  # not eligible - age boundary
    when((dataset.age >= 5) & (dataset.age < 16)).then("5-15"),  # eligible by age, relevant for pregnancy exclusion
    when((dataset.age >= 16) & (dataset.age < 17)).then("16"),  # eligible by age, useful boundary check
    when((dataset.age >= 17) & (dataset.age <= 64)).then("17-64"),  # eligible by age
    when(dataset.age > 64).then("65+"),  # eligible by age
)

measures.define_measure(
    name="sorethroat_eligible_among_base",
    numerator=dataset.include_patient_sore_throat,
    denominator=measure_base_population,
    group_by={"age_band_sorethroat": age_band_sorethroat},
)

sorethroat_excluded_population = (
    measure_base_population
    & ~dataset.include_patient_sore_throat
)

measures.define_measure(
    name="sorethroat_excluded_among_base_by_age_band",
    numerator=~dataset.include_patient_sore_throat,
    denominator=measure_base_population,
    group_by={"age_band_sorethroat": age_band_sorethroat},
)

measures.define_measure(
    name="sorethroat_excluded_among_base_due_to_pregnant_female_under16",
    numerator=(
        dataset.pregnant_this_month
        & (dataset.sex == "female")
        & (dataset.age < 16)
    ),
    denominator=sorethroat_excluded_population,
)

sorethroat_pf_user_population = (
    (dataset.numerator_pf_consultation_sorethroat > 0)
    & measure_base_population
)

measures.define_measure(
    name="sorethroat_pf_users_not_eligible",
    numerator=~dataset.include_patient_sore_throat,
    denominator=sorethroat_pf_user_population,
)

measures.define_measure(
    name="sorethroat_pf_users_not_eligible_by_age_band",
    numerator=~dataset.include_patient_sore_throat,
    denominator=sorethroat_pf_user_population,
    group_by={"age_band_sorethroat": age_band_sorethroat},
)

measures.define_measure(
    name="sorethroat_pf_users_not_eligible_by_sex_age_pregnancy",
    numerator=~dataset.include_patient_sore_throat,
    denominator=sorethroat_pf_user_population,
    group_by={
        "sex": dataset.sex,
        "age_band_sorethroat": age_band_sorethroat,
        "pregnant": dataset.pregnant,
    },
)


'''
Insect bites:
    - Inclusion: age >= 1
    - Exclusion: pregnant female under 16s

Checks:
- Among patients with at least one PF insect bite consultation, what proportion were classified as not eligible?
- Break down apparent ineligibility by age band and pregnancy-related exclusion.
'''
age_band_insectbite = case(
    when(dataset.age.is_null()).then("Missing"),
    when(dataset.age < 1).then("<1"),  # not eligible
    when((dataset.age >= 1) & (dataset.age < 16)).then("1-15"),  # eligible by age, relevant for pregnancy exclusion
    when((dataset.age >= 16) & (dataset.age < 17)).then("16"),  # eligible by age, useful boundary check
    when((dataset.age >= 17) & (dataset.age <= 64)).then("17-64"),  # eligible by age
    when(dataset.age > 64).then("65+"),  # eligible by age
)

measures.define_measure(
    name="insectbite_eligible_among_base",
    numerator=dataset.include_patient_insect_bites,
    denominator=measure_base_population,
    group_by={"age_band_insectbite": age_band_insectbite},
)

insectbite_excluded_population = (
    measure_base_population
    & ~dataset.include_patient_insect_bites
)

measures.define_measure(
    name="insectbite_excluded_among_base_by_age_band",
    numerator=~dataset.include_patient_insect_bites,
    denominator=measure_base_population,
    group_by={"age_band_insectbite": age_band_insectbite},
)

measures.define_measure(
    name="insectbite_excluded_among_base_due_to_pregnant_female_under16",
    numerator=(
        dataset.pregnant_this_month
        & (dataset.sex == "female")
        & (dataset.age < 16)
    ),
    denominator=insectbite_excluded_population,
)

insectbite_pf_user_population = (
    (dataset.numerator_pf_consultation_insectbite > 0)
    & measure_base_population
)

measures.define_measure(
    name="insectbite_pf_users_not_eligible",
    numerator=~dataset.include_patient_insect_bites,
    denominator=insectbite_pf_user_population,
)

measures.define_measure(
    name="insectbite_pf_users_not_eligible_by_age_band",
    numerator=~dataset.include_patient_insect_bites,
    denominator=insectbite_pf_user_population,
    group_by={"age_band_insectbite": age_band_insectbite},
)

measures.define_measure(
    name="insectbite_pf_users_not_eligible_by_sex_age_pregnancy",
    numerator=~dataset.include_patient_insect_bites,
    denominator=insectbite_pf_user_population,
    group_by={
        "sex": dataset.sex,
        "age_band_insectbite": age_band_insectbite,
        "pregnant": dataset.pregnant,
    },
)


'''
Shingles:
    - Inclusion: age >= 18
    - Exclusion: pregnant female

Checks:
- Among patients with at least one PF shingles consultation, what proportion were classified as not eligible?
- Break down apparent ineligibility by age band and pregnancy-related exclusion.
'''
age_band_shingles = case(
    when(dataset.age.is_null()).then("Missing"),
    when(dataset.age < 1).then("<1"),  # not eligible
    when((dataset.age >= 1) & (dataset.age < 17)).then("1-16"),  # not eligible
    when((dataset.age >= 17) & (dataset.age < 18)).then("17"),  # not eligible - age boundary
    when((dataset.age >= 18) & (dataset.age <= 64)).then("18-64"),  # eligible by age
    when(dataset.age > 64).then("65+"),  # eligible by age
)

measures.define_measure(
    name="shingles_eligible_among_base",
    numerator=dataset.include_patient_shingles,
    denominator=measure_base_population,
    group_by={"age_band_shingles": age_band_shingles},
)

shingles_excluded_population = (
    measure_base_population
    & ~dataset.include_patient_shingles
)

measures.define_measure(
    name="shingles_excluded_among_base_by_age_band",
    numerator=~dataset.include_patient_shingles,
    denominator=measure_base_population,
    group_by={"age_band_shingles": age_band_shingles},
)

measures.define_measure(
    name="shingles_excluded_among_base_due_to_pregnant_female",
    numerator=(
        dataset.pregnant_this_month
        & (dataset.sex == "female")
    ),
    denominator=shingles_excluded_population,
)

shingles_pf_user_population = (
    (dataset.numerator_pf_consultation_shingles > 0)
    & measure_base_population
)

shingles_pf_user_not_eligible_population = (
    shingles_pf_user_population
    & ~dataset.include_patient_shingles
)

measures.define_measure(
    name="shingles_pf_users_not_eligible",
    numerator=~dataset.include_patient_shingles,
    denominator=shingles_pf_user_population,
)

measures.define_measure(
    name="shingles_pf_users_not_eligible_by_age_band",
    numerator=~dataset.include_patient_shingles,
    denominator=shingles_pf_user_population,
    group_by={"age_band_shingles": age_band_shingles},
)

measures.define_measure(
    name="shingles_pf_users_not_eligible_due_to_pregnant_female",
    numerator=(
        dataset.pregnant_this_month
        & (dataset.sex == "female")
    ),
    denominator=shingles_pf_user_not_eligible_population,
)

measures.define_measure(
    name="shingles_pf_users_not_eligible_by_sex_age_pregnancy",
    numerator=~dataset.include_patient_shingles,
    denominator=shingles_pf_user_population,
    group_by={
        "sex": dataset.sex,
        "age_band_shingles": age_band_shingles,
        "pregnant": dataset.pregnant,
    },
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

age_band_impetigo = age_band_insectbite

measures.define_measure(
    name="impetigo_eligible_among_base",
    numerator=dataset.include_patient_impetigo,
    denominator=measure_base_population,
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


# Overall PF eligibility
measures.define_measure(
    name="pf_overall_eligible_among_base",
    numerator=dataset.include_patient_overall_eligible,
    denominator=measure_base_population,
    group_by={"age_band_pregnancy_validation": age_band_pregnancy_validation},
)

measures.define_measure(
    name="pf_overall_user_not_eligible",
    numerator=~dataset.include_patient_overall_eligible,
    denominator=pf_user_population,
)