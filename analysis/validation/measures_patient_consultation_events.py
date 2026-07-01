from ehrql import case, create_measures, months, when
from analysis.dataset_definition_patients_measures import dataset
# opensafely exec ehrql:v1 generate-measures analysis/measures_patient.py --output output/measures_patient.csv

measures = create_measures()
measures.configure_disclosure_control(enabled=False)
measures.define_defaults(
    intervals=months(2).starting_on("2025-10-01"),
    # intervals=months(2).starting_on("2024-02-01")
)

measure_base_population = (
    # dataset.alive
    dataset.sex.is_in(["male","female"])
    # & dataset.registered_start
    & dataset.registered_index
    # & (dataset.age <= 120)
)

measures.define_measure(
    name="pf_consultation_general_total",
    numerator=dataset.pf_consultation_general,
    denominator=measure_base_population,
)
measures.define_measure(
    name="pf_consultation_general_butno_condition_total",
    numerator=dataset.pf_consultation_general_butno_condition,
    denominator=measure_base_population,
)
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
    name="pf_consultation_condition_sum_total",
    numerator=pf_condition_consultation_sum,
    denominator=measure_base_population,
)

pf_conditions = [
    "uti",
    "sinusitis",
    "insectbite",
    "otitismedia",
    "sorethroat",
    "shingles",
    "impetigo",
]

for condition in pf_conditions:

    # check numerator only
    measures.define_measure(
        name=f"pf_event_{condition}",
        numerator=getattr(dataset, f"numerator_pf_event_{condition}"),
        denominator=measure_base_population,
    )

    # check numerator only
    measures.define_measure(
        name=f"pf_consultation_{condition}",
        numerator=getattr(dataset, f"numerator_pf_consultation_{condition}"),
        denominator=measure_base_population,
    )

    # check numerator only
    measures.define_measure(
        name=f"pf_date_{condition}",
        numerator=getattr(dataset, f"numerator_pf_date_{condition}"),
        denominator=measure_base_population,
    )

gp_conditions = [
    "uti",
    "sinusitis",
    "insectbite",
    "insectbite_strict",
    "otitismedia",
    "sorethroat",
    "shingles",
    "impetigo",
]

for condition in gp_conditions:

    # check numerator only
    measures.define_measure(
        name=f"gp_consultation_{condition}",
        numerator=getattr(dataset, f"numerator_gp_consultation_{condition}"),
        denominator=measure_base_population,
    )

pf_condition_map = {
    "uti": "uuti",
    "sinusitis": "sinusitis",
    "insectbite": "insect_bites",
    "otitismedia": "otitis_media",
    "sorethroat": "sore_throat",
    "shingles": "shingles",
    "impetigo": "impetigo",
}

for condition, eligibility_name in pf_condition_map.items():

    # Among patients with ≥1 PF consultation for a given condition, 
    # the proportion that meets the corresponding PF eligibility criteria.
    measures.define_measure(
        name=f"pf_{condition}_eligible_among_pf_consultation",
        numerator=getattr(dataset, f"include_patient_{eligibility_name}"),
        denominator=(
            getattr(dataset, f"numerator_pf_consultation_{condition}") > 0
        ) & measure_base_population,
    )