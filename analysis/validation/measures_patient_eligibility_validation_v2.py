from ehrql import create_dataset, create_measures, show, days, weeks, months, years, case, when, get_parameter, INTERVAL
from ehrql.tables.tpp import (patients, practice_registrations, clinical_events, addresses, 
                              ethnicity_from_sus,
                              emergency_care_attendances,appointments)
import analysis.codelists as codelists

from analysis.pf_variable_library import (get_imd, get_latest_ethnicity, 
                                          select_events_between, select_events_from_codelist, select_events_by_consultation_id,
                                          has_event_count, ae_non_primary_diagnosis_matches)
from ehrql import claim_permissions
claim_permissions("appointments")

dataset = create_dataset()
dataset.configure_dummy_data(population_size=500)

# One month time period (to start with this is Nov 25) 
start_date = INTERVAL.start_date    
index_date = INTERVAL.end_date

########################################################
# Patient identifiers: alive_status, registration_status
alive = patients.is_alive_on(index_date) # alive at the end of month
# Only include the patient if they were registered for the whole month, 
# so registered before the month starts and not deregistered or died during the month
registered_start = practice_registrations.for_patient_on(start_date).exists_for_patient()
registered_index = practice_registrations.for_patient_on(index_date).exists_for_patient()

# Demographics: sex, age, patient_imd
sex = patients.sex
age = patients.age_on(index_date)

# Define population
# base_population = patients.exists_for_patient()
age_valid = (patients.age_on(index_date) <= 120) # "Exclude any patients over 120 years old as the date of birth is most likely to be missing"
base_population = alive & registered_start & registered_index & age_valid 
# dataset.define_population(base_population) # include all patients or those alive and registered
dataset.define_population(patients.exists_for_patient())

dataset.start_date = start_date
dataset.index_date = index_date
dataset.registered_start = registered_start
dataset.registered_index = registered_index
dataset.alive = alive
dataset.sex = sex
dataset.age = age
dataset.date_of_birth = patients.date_of_birth # debug

dataset.imd = get_imd(addresses, index_date)
dataset.ethnicity = get_latest_ethnicity(index_date,clinical_events,codelists.ethnicity_group16_codelist,ethnicity_from_sus,grouping=16,)
# Patient identifiers: practice_id, stp, region
dataset.practice = practice_registrations.for_patient_on(index_date).practice_pseudo_id
dataset.stp = practice_registrations.for_patient_on(index_date).practice_stp
# dataset.region = practice_registrations.for_patient_on(index_date).practice_nuts1_region_name
dataset.region = case(
    when(practice_registrations.for_patient_on(index_date).practice_nuts1_region_name.is_null()).then("Missing"),
    otherwise=practice_registrations.for_patient_on(index_date).practice_nuts1_region_name,
)
########################################################
'''
This section counts the number of PF consultations for each condition.
Outputs:
- pf_consultation_general: consultation count where their clinical events have any of the three general PF codes
- pf_consultation_general_butno_condition: consultation count where their clinical events have any of the three general PF codes BUT no PF condition codes
- numerator_pf_consultation_{name}: number of PF consultations for a specific PF condition
- numerator_pf_date_{name}: number of PF consultation dates for a specific PF condition
'''

selected_events = select_events_between(clinical_events, start_date, index_date)
pf_consultation_events = select_events_from_codelist(selected_events, codelists.pf_consultation_events_dict["pf_consultation_services_combined"])
# 'pf_ids' is a set of consultation ids where their clinical events have any of the three general PF codes
pf_ids = pf_consultation_events.consultation_id
selected_pf_id_events = select_events_by_consultation_id(selected_events, pf_ids)

# dataset.has_pf_consultation = pf_consultation_events.exists_for_patient()
dataset.pf_consultation_general = pf_consultation_events.consultation_id.count_distinct_for_patient()

pf_conditions_pf_codes = {
    "uti": codelists.uti_code,
    "sinusitis": codelists.sinusitis_code,
    "insectbite": codelists.insectbite_code,
    "otitismedia": codelists.otitismedia_code,
    "sorethroat": codelists.sorethroat_code,
    "shingles": codelists.shingles_code,
    "impetigo": codelists.impetigo_code,
}

# a set of codes for any PF condition
pf_conditions_pf_code_set = []
for codes in pf_conditions_pf_codes.values():
    pf_conditions_pf_code_set += codes

# select events with both general PF codes and PF condition codes
pf_condition_events = selected_pf_id_events.where(selected_pf_id_events.snomedct_code.is_in(pf_conditions_pf_code_set))
# extract consultation IDs for these events
pf_condition_consultation_ids = pf_condition_events.consultation_id
# select PF consultation events (those with general PF codes) that the consultation id is not in the set of consultation ids with condition codes
pf_consultations_general_butno_condition_events = pf_consultation_events.where(
    ~pf_consultation_events.consultation_id.is_in(pf_condition_consultation_ids)
)
# count number of consultations from the above event selection
dataset.pf_consultation_general_butno_condition = (
    pf_consultations_general_butno_condition_events.consultation_id.count_distinct_for_patient()
)

for name, codes in pf_conditions_pf_codes.items():
    # count consultations and consultation dates
    count_pf_consultation, count_pf_date = has_event_count(selected_pf_id_events, codes)
    setattr(dataset, f"numerator_pf_consultation_{name}", count_pf_consultation)
    setattr(dataset, f"numerator_pf_date_{name}", count_pf_date)

########################################################
"""
Clinical variables for eligible population denominator:
- pregnant_this_month
- bullous_impetigo_this_month
- recurrent_impetigo_this_year
- catheter_status
- recurrent_uti
"""

from analysis.pf_variable_library import check_code_in_time_window, check_recurrent_status
# -- pregnancy_status - naive version
# pregnant_this_month = check_code_in_time_window(index_date-months(1),index_date, clinical_events, codelists.gp_snomed_codelist_pregnancy)
# dataset.pregnant_this_month = pregnant_this_month
# -- pregancy_status developed by Helen
# look back for recent end-of-pregnancy codes -- assume no longer pregnant if in last 12 weeks
dataset.pregnancy_end_recent = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.gp_snomed_codelist_end_pregnancy) &
    clinical_events.date.is_on_or_between(start_date - weeks(32), start_date - days(1))
    ).sort_by(clinical_events.date).last_for_patient().date
# look ahead 40 weeks for end-of-pregnancy codes
dataset.pregnancy_end = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.gp_snomed_codelist_end_pregnancy) &
    clinical_events.date.is_on_or_between(start_date, start_date + weeks(40))
    ).sort_by(clinical_events.date).first_for_patient().date
# estimated date of delivery (EDD) - very recent or in future to estimate the known start of pregnancy
dataset.pregnancy_edd = clinical_events.where(
    clinical_events.date.is_on_or_between(start_date - weeks(2), start_date + weeks(34)) &
    clinical_events.snomedct_code.is_in(codelists.gp_snomed_codelist_pregnancy_edd)
    ).sort_by(clinical_events.date).first_for_patient().date
# recent "pregnant" codes - this is to be used where no delivery or EDD recorded
dataset.pregnancy_code = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.gp_snomed_codelist_pregnancy) &
    clinical_events.date.is_on_or_between(start_date - weeks(12), start_date + weeks(4))
    ).sort_by(clinical_events.date).first_for_patient().date
# combine criteria to create a pregnancy status for the current month:
dataset.pregnant = case(
    # recent delivery -> not pregnant now:
    when(dataset.pregnancy_end_recent.is_on_or_after(start_date - weeks(12))).then("0-R"),
    # EDD in month or next 8 months, not preceeded by an end-of-pregnancy
    when(dataset.pregnancy_edd.is_not_null() 
        # check that the pregnancy linked to the EDD did not end very early,
        # i.e prior to the last 12 weeks which is already captured above
         & (dataset.pregnancy_end_recent.is_null() # no past delivery captured
            | ~dataset.pregnancy_end_recent.is_on_or_between(dataset.pregnancy_edd-weeks(28),dataset.pregnancy_edd+weeks(3))
            )).then("P-EDD"),
    # end of pregnancy in month or next 2 months - currently pregnant:
    when(dataset.pregnancy_end.is_on_or_before(start_date + weeks(12))).then("P-E"),
    # recent pregnancy code
    when(dataset.pregnancy_code.is_not_null()).then("P"),
    otherwise="0",)
# pregnant_this_month = dataset.pregnant.is_in(("P-E", "P-EDD", "P"))
# Age <= 11: pregnancy flags are considered too unreliable and are not counted as pregnant.
pregnant_this_month = (dataset.pregnant.is_in(("P-E", "P-EDD", "P")) & (age >= 12))
dataset.pregnant_this_month = pregnant_this_month

# Anchor date for impetigo exclusion
# anchor is the day before the monthly interval start
impetigo_exclusion_anchor_date = start_date

# bullous_impetigo in one month
# When start_date = 2025-10-01, impetigo_exclusion_anchor_date = 2025-10-01
# the lookback window is [2025-09-01, 2025-09-30]
# bullous_impetigo_this_month = check_code_in_time_window(start_date,index_date,clinical_events,codelists.gp_snomed_codelist_bullous_impetigo)
bullous_impetigo_last_month = check_code_in_time_window(
    impetigo_exclusion_anchor_date-months(1),
    impetigo_exclusion_anchor_date-days(1),
    clinical_events,
    codelists.gp_snomed_codelist_bullous_impetigo)
dataset.bullous_impetigo_last_month = bullous_impetigo_last_month

# recurrent_impetigo: (defined as 2 or more episodes in one year) 
# episodes are distinguished using 4 weeks gap, so any codes within 4 weeks are considered to be part of the same episode.
# For recurrent eligibility criteria, 
# we use the start of the study month as the anchor date and exclude the study month from the lookback window. 
# Therefore, criteria defined over N months are implemented as N-1 months before the anchor date, 
# ending on the day before the study month starts.
recurrent_impetigo_window_start = impetigo_exclusion_anchor_date - months(11)
recurrent_impetigo_window_end = impetigo_exclusion_anchor_date - days(1) 
recurrent_impetigo_window_end_buffer = impetigo_exclusion_anchor_date - days(8)# one week buffer
recurrent_impetigo_12m = check_recurrent_status(
    recurrent_impetigo_window_start, 
    # recurrent_impetigo_window_end,
    recurrent_impetigo_window_end_buffer,
    clinical_events, 
    codelists.gp_snomed_codelist_impetigo,
    gap_weeks=4, 
    min_episodes=2)
dataset.recurrent_impetigo_12m = recurrent_impetigo_12m

# Anchor date for uti exclusion
# anchor is the day before the monthly interval start
uti_exclusion_anchor_date = start_date

# catheter_status: excluding patients who clearly have a catheter, and for following 12 months after code is included
catheter_12m = check_code_in_time_window(
    uti_exclusion_anchor_date - months(11),
    uti_exclusion_anchor_date - days(1),
    clinical_events,
    codelists.gp_snomed_codelist_urinary_catheter,
)
dataset.catheter_12m = catheter_12m

# recurrent_uti: (2 episodes in last 6 months, or 3 episodes in last 12 months) an episode is defined as a 4 week period, so any codes within this time are considered to be part of the same episode.
# To avoid counting consultations in the study month itself, 
# criteria defined over N months are implemented as N-1 months before the anchor date, 
# ending on the day before the study month starts.
recurrent_uti_6m_window_start = uti_exclusion_anchor_date - months(5)
recurrent_uti_12m_window_start = uti_exclusion_anchor_date - months(11)
recurrent_uti_window_end = uti_exclusion_anchor_date - days(1) 
recurrent_uti_window_end_buffer = uti_exclusion_anchor_date - days(8)# one week buffer
recurrent_uti_6m = check_recurrent_status(
    recurrent_uti_6m_window_start, 
    # recurrent_uti_window_end,
    recurrent_uti_window_end_buffer,
    clinical_events, 
    codelists.gp_snomed_codelist_uti,
    gap_weeks=4, 
    min_episodes=2)
recurrent_uti_12m = check_recurrent_status(
    recurrent_uti_12m_window_start, 
    # recurrent_uti_window_end,
    recurrent_uti_window_end_buffer,
    clinical_events, 
    codelists.gp_snomed_codelist_uti,
    gap_weeks=4, 
    min_episodes=3)
recurrent_uti = recurrent_uti_6m | recurrent_uti_12m
dataset.recurrent_uti_6m = recurrent_uti_6m
dataset.recurrent_uti_12m = recurrent_uti_12m
dataset.recurrent_uti = recurrent_uti

########################################################
"""
Eligibility/clinical characteristics flag for study population denominator:
- include_patient_otitis_media
- include_patient_sinusitis
- include_patient_sore_throat
- include_patient_insect_bites
- include_patient_shingles
- include_patient_impetigo
- include_patient_uti
- include_patient_overall_eligible
"""
female = patients.sex.is_in(["female"])

# Condition: acute otitis media
# - inclusion: children aged 1 to 17 years
# - exclusion: none
include_patient_otitis_media = (age >= 1) & (age <= 17) 
dataset.include_patient_otitis_media = include_patient_otitis_media

# Condition: acute sinusitis
# - inclusion: age >= 12
# - exclusion: none
include_patient_sinusitis = (age >= 12)
dataset.include_patient_sinusitis = include_patient_sinusitis

# Condition: acute sore throat
# - inclusion: age >= 5
# - exclusion: pregnant female under 16s
age_eligible_sore_throat = (age >= 5)
exclusion_sore_throat = pregnant_this_month & (age < 16) & (female)
include_patient_sore_throat = (age_eligible_sore_throat & ~exclusion_sore_throat)
dataset.include_patient_sore_throat = include_patient_sore_throat

# Condition: infected insect bites
# - inclusion: age >= 1
# - exclusion: pregnant female under 16s
age_eligible_insect_bites = (age >= 1)
exclusion_insect_bites = pregnant_this_month & (age < 16) & (female)
include_patient_insect_bites = (age_eligible_insect_bites & ~exclusion_insect_bites)
dataset.include_patient_insect_bites = include_patient_insect_bites

# Condition: shingles
# - inclusion: age >= 18
# - exclusion: pregnant female
age_eligible_shingles = (age >= 18)
exclusion_shingles = pregnant_this_month & (female)
include_patient_shingles = (age_eligible_shingles & ~exclusion_shingles)
dataset.include_patient_shingles = include_patient_shingles

# Condition: impetigo
# - inclusion: age >= 1
# - exclusion: 
# - - bullous impetigo, 
# - - recurrent impetigo (defined as 2 or more episodes in the same year), 
# - - pregnant female under 16 years
impetigo_age_eligible = (age >= 1)
impetigo_exclusion = (bullous_impetigo_last_month | recurrent_impetigo_12m | (pregnant_this_month & (age < 16) & female))
include_patient_impetigo = (impetigo_age_eligible & ~impetigo_exclusion)
dataset.include_patient_impetigo = include_patient_impetigo

# Condition: Uncomplicated UTI
# - inclusion: women aged 16 to 64 years
# - exclusion: 
# - - pregnant female
# - - urinary catheter
# - - recurrent UTI: 2 episodes in last 6 months, or 3 episodes in last 12 months
uuti_eligible = (age >= 16) & (age <= 64) & female
uuti_exclusion = (pregnant_this_month | catheter_12m | recurrent_uti)
include_patient_uuti = (uuti_eligible & ~uuti_exclusion)
dataset.include_patient_uuti = include_patient_uuti

# include_patient_overall_eligible
include_patient_overall_eligible = (include_patient_otitis_media|include_patient_sinusitis
                                  |include_patient_sore_throat|include_patient_insect_bites
                                  |include_patient_shingles|include_patient_impetigo|include_patient_uuti)
dataset.include_patient_overall_eligible = include_patient_overall_eligible

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
    # numerator=dataset.pregnant_this_month,
    numerator=measure_base_population,
    denominator=measure_base_population,
    group_by={"pregnant": dataset.pregnant},
)

measures.define_measure(
    name="pregnancy_among_base_by_sex_age",
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

# measures.define_measure(
#     name="base_by_otitismedia_age_band",
#     numerator=measure_base_population,
#     denominator=measure_base_population,
#     group_by={"age_band_otitismedia": age_band_otitismedia},
# )

measures.define_measure(
    name="otitismedia_eligible_among_base",
    numerator=dataset.include_patient_otitis_media,
    denominator=measure_base_population,
    # group_by={"age_band_otitismedia": age_band_otitismedia},
)

measures.define_measure(
    name="otitismedia_eligible_among_base_by_age",
    numerator=dataset.include_patient_otitis_media,
    denominator=measure_base_population,
    group_by={"age_band_otitismedia": age_band_otitismedia},
)

measures.define_measure(
    name="otitismedia_excluded_among_base",
    numerator=~dataset.include_patient_otitis_media,
    denominator=measure_base_population,
    # group_by={"age_band_otitismedia": age_band_otitismedia},
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
    numerator=dataset.bullous_impetigo_last_month,
    denominator=measure_base_population,
)

measures.define_measure(
    name="recurrent_impetigo_among_base",
    numerator=dataset.recurrent_impetigo_12m,
    denominator=measure_base_population,
)

measures.define_measure(
    name="bullous_and_recurrent_impetigo_among_base",
    numerator=dataset.bullous_impetigo_last_month & dataset.recurrent_impetigo_12m,
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
    numerator=dataset.bullous_impetigo_last_month,
    denominator=impetigo_excluded_population,
)

measures.define_measure(
    name="impetigo_excluded_among_base_due_to_recurrent",
    numerator=dataset.recurrent_impetigo_12m,
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
    numerator=dataset.bullous_impetigo_last_month,
    denominator=impetigo_pf_user_not_eligible_population,
)

measures.define_measure(
    name="impetigo_pf_users_not_eligible_due_to_recurrent",
    numerator=dataset.recurrent_impetigo_12m,
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
    numerator=dataset.catheter_12m,
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
    numerator=dataset.catheter_12m,
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
    numerator=dataset.catheter_12m,
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