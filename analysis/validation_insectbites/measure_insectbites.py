"""
Compare GP insect bite consultation definitions.

For each definition, calculate:
- Number of patients with at least one consultation
- Number of consultations

Definitions:
- P2 infected insect bite codelist
- Strict infected insect bite codelist
- All insect bite codelist
- Cellulitis-only codelist
- All insect bite code plus a cellulitis code within the same consultation
"""

from ehrql import create_measures, months
from analysis.validation_insectbites.dataset_definition_patients_measures import dataset
# opensafely exec ehrql:v1 generate-measures analysis/measures_patient.py --output output/measures_patient.csv

measures = create_measures()
measures.configure_disclosure_control(enabled=False)
measures.define_defaults(
    intervals=months(2).starting_on("2025-10-01"),
)

measure_base_population = (
    dataset.alive
    & dataset.registered_start
    & dataset.registered_index
    & (dataset.age <= 120)
)

insectbite_definitions = {
    "insectbite": dataset.numerator_gp_consultation_insectbite,
    "insectbite_strict": dataset.numerator_gp_consultation_insectbite_strict,
    "insectbite_all": dataset.numerator_gp_consultation_insectbite_all,
    "cellulitis_only": dataset.numerator_gp_consultation_cellulitis_only,
    "insectbite_strict_or_all": dataset.numerator_gp_consultation_insectbite_strict_or_all,
    "insectbite_all_plus_cellulitis":dataset.numerator_gp_consultation_insectbite_all_plus_cellulitis,
    "insectbite_strict_or_all_plus_cellulitis":dataset.numerator_gp_consultation_insectbite_strict_or_all_plus_cellulitis,
}

for name, consultation_count in insectbite_definitions.items():

    # Number of patients with >=1 consultation
    measures.define_measure(
        name=f"n_patients_{name}",
        numerator=consultation_count > 0,
        denominator=measure_base_population,
    )

    # Number of consultations
    measures.define_measure(
        name=f"n_consultations_{name}",
        numerator=consultation_count,
        denominator=measure_base_population,
    )

