from ehrql import case, create_measures, months, when
from analysis.validation_econsultations.dataset_definition_patients_measures import dataset
# opensafely exec ehrql:v1 generate-measures analysis/measures_patient.py --output output/measures_patient.csv

measures = create_measures()
measures.configure_disclosure_control(enabled=False)
measures.define_defaults(
    intervals=months(1).starting_on("2025-10-01"),
    # intervals=months(2).starting_on("2024-02-01")
)

# The denominator is the general eligible registered population for the interval:
measure_base_population = (
    dataset.alive
    & dataset.registered_start
    & dataset.registered_index
    & (dataset.age <= 120)
)

'''
Checks:
- For each condition:
  gp_<condition>_patient_date_f2f
  + gp_<condition>_patient_date_online
  + gp_<condition>_patient_date_telephone
  + gp_<condition>_patient_date_othermode
  should equal gp_<condition>_patient_date_total.

- For all PF-related GP conditions combined:
  gp_pf_patient_date_f2f
  + gp_pf_patient_date_online
  + gp_pf_patient_date_telephone
  + gp_pf_patient_date_othermode
  should equal gp_pf_patient_date_total.

- Across individual conditions:
  sum(gp_<condition>_patient_date_<mode>) can be compared with gp_pf_patient_date_<mode>.
  If the condition-specific sum is larger, this suggests overlap between
  condition-specific GP codelists on the same patient-date.

Notes:
- These are patient-date counts, not distinct consultation-ID counts.
- numerator_gp_consultation_<condition> remains a separate consultation-ID-based variable.
'''

gp_modes = [
    "f2f",
    "online",
    "telephone",
    "econsultation",
    "othermode",
]

# gp_conditions = [
#     "uti",
#     "sinusitis",
#     "insectbite",
#     "otitismedia",
#     "sorethroat",
#     "shingles",
#     "impetigo",
# ]

# gp_pf_patient_date_<mode> counts PF-related GP condition patient-dates by consultation mode
# - distinct patient-dates with at least one PF-related GP condition code;
# - classified by consultation mode using same-patient same-date mode codes;
# - all seven PF-related GP conditions are combined.
for mode in gp_modes:
    measures.define_measure(
        name=f"gp_pf_patient_date_{mode}",
        numerator=getattr(dataset, f"gp_pf_patient_date_{mode}"),
        denominator=measure_base_population,
    )

# Total number of PF-related GP condition patient-dates before mode classification.
# This should equal the sum of the four mode-specific patient-date measures.
measures.define_measure(
    name="gp_pf_patient_date_total",
    numerator=dataset.gp_pf_patient_date_total,
    denominator=measure_base_population,
)

# Validation measure:
# gp_pf_patient_date_f2f
# + gp_pf_patient_date_online
# + gp_pf_patient_date_telephone
# + gp_pf_patient_date_othermode.
# This should equal gp_pf_patient_date_total.
measures.define_measure(
    name="gp_pf_patient_date_mode_sum",
    numerator=dataset.gp_pf_patient_date_mode_sum,
    denominator=measure_base_population,
)

# # For each PF-related condition, two types of measures are produced:
# # - original consultation totals (based on consultation ids): gp_consultation_<condition>_total
# # - patient-date counts by mode
# #   - gp_<condition>_patient_date_<mode>
# #   - gp_<condition>_patient_date_total
# #   - gp_<condition>_patient_date_mode_sum
# #   --- _total should equal _mode_sum
# for condition in gp_conditions:
#     # Original GP consultation-ID-based count for this condition
#     measures.define_measure(
#         name=f"gp_consultation_{condition}_total",
#         numerator=getattr(dataset, f"numerator_gp_consultation_{condition}"),
#         denominator=measure_base_population,
#     )

#     # New GP condition patient-date count for this condition
#     measures.define_measure(
#         name=f"gp_{condition}_patient_date_total",
#         numerator=getattr(dataset, f"gp_{condition}_patient_date_total"),
#         denominator=measure_base_population,
#     )

#     measures.define_measure(
#         name=f"gp_{condition}_patient_date_mode_sum",
#         numerator=getattr(dataset, f"gp_{condition}_patient_date_mode_sum"),
#         denominator=measure_base_population,
#     )

#     # GP condition patient-date count by mode
#     for mode in gp_modes:
#         measures.define_measure(
#             name=f"gp_{condition}_patient_date_{mode}",
#             numerator=getattr(dataset, f"gp_{condition}_patient_date_{mode}"),
#             denominator=measure_base_population,
#         )

# control_conditions = [
#     "lowerbackpain",
# ]

# for condition in control_conditions:
#     measures.define_measure(
#         name=f"gp_consultation_{condition}_total",
#         numerator=getattr(dataset, f"numerator_gp_consultation_{condition}"),
#         denominator=measure_base_population,
#     )

#     measures.define_measure(
#         name=f"gp_{condition}_patient_date_total",
#         numerator=getattr(dataset, f"gp_{condition}_patient_date_total"),
#         denominator=measure_base_population,
#     )

#     measures.define_measure(
#         name=f"gp_{condition}_patient_date_mode_sum",
#         numerator=getattr(dataset, f"gp_{condition}_patient_date_mode_sum"),
#         denominator=measure_base_population,
#     )

#     for mode in gp_modes:
#         measures.define_measure(
#             name=f"gp_{condition}_patient_date_{mode}",
#             numerator=getattr(dataset, f"gp_{condition}_patient_date_{mode}"),
#             denominator=measure_base_population,
#         )