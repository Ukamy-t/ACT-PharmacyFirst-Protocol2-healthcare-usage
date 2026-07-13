from ehrql import create_measures, months
from analysis.dataset_definition_patients_measures import dataset

# opensafely exec ehrql:v1 generate-measures analysis/measures_patient.py --output output/measures_patient.csv

measures = create_measures()
measures.configure_disclosure_control(enabled=False)

measures.define_defaults(
    intervals=months(1).starting_on("2025-10-01"),
)

# Our original population
measure_base_population_original = (
    dataset.alive
    & dataset.registered_start
    & dataset.registered_index
    & (dataset.age <= 120)
)

# Monthly Dashboard population
measure_base_population_dashboard = (
    dataset.sex.is_in(["male", "female"])
    & dataset.registered_index
)

# How many patients in the dashboard population meet or do not meet each criterion.
# Which eligibility criteria differ most at the patient level?

measures.define_measure(
    name="dashoboard_base_pop_alivestart",
    numerator=dataset.alive_start,
    denominator=measure_base_population_dashboard,
)

measures.define_measure(
    name="dashoboard_base_pop_aliveindex",
    numerator=dataset.alive,
    denominator=measure_base_population_dashboard,
)

measures.define_measure(
    name="dashoboard_base_pop_registeredstart",
    numerator=dataset.registered_start,
    denominator=measure_base_population_dashboard,
)

measures.define_measure(
    name="dashoboard_base_pop_eligibleage",
    numerator=dataset.age <= 120,
    denominator=measure_base_population_dashboard,
)

# Which criterion actually explains the consultation difference?

pf_condition_consultation_sum = (
    dataset.numerator_pf_consultation_uti
    + dataset.numerator_pf_consultation_sinusitis
    + dataset.numerator_pf_consultation_insectbite
    + dataset.numerator_pf_consultation_otitismedia
    + dataset.numerator_pf_consultation_sorethroat
    + dataset.numerator_pf_consultation_shingles
    + dataset.numerator_pf_consultation_impetigo
)

measures.define_measure(
    name="pf_condition_sum_dashboard",
    numerator=pf_condition_consultation_sum,
    denominator=measure_base_population_dashboard,
)

measures.define_measure(
    name="pf_condition_sum_dashboard_alivestart",
    numerator=pf_condition_consultation_sum,
    denominator=(
        measure_base_population_dashboard
        & dataset.alive_start
    ),
)

measures.define_measure(
    name="pf_condition_sum_dashboard_alive",
    numerator=pf_condition_consultation_sum,
    denominator=(
        measure_base_population_dashboard
        & dataset.alive
    ),
)

measures.define_measure(
    name="pf_condition_sum_dashboard_alive_registered_start",
    numerator=pf_condition_consultation_sum,
    denominator=(
        measure_base_population_dashboard
        & dataset.alive
        & dataset.registered_start
    ),
)

measures.define_measure(
    name="pf_condition_sum_dashboard_all_original_criteria",
    numerator=pf_condition_consultation_sum,
    denominator=(
        measure_base_population_dashboard
        & dataset.alive
        & dataset.registered_start
        & (dataset.age <= 120)
    ),
)