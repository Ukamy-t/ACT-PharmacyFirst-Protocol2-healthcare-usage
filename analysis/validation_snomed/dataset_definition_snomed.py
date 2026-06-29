# analysis/dataset_definition_snomed_validation.py
# opensafely run generate_dataset_snomed_count
# gunzip -c output/dataset_patients_snomed.csv.gz > output/dataset_patients_snomed.csv
# gunzip -c output/dataset_patients_snomed_insectbite.csv.gz > output/dataset_patients_snomed_insectbite.csv

from ehrql import create_dataset, get_parameter, days, weeks, months, show, case, when
from ehrql.tables.tpp import (patients, practice_registrations, clinical_events)
import analysis.codelists as codelists
from analysis.pf_variable_library import (select_events_between, select_events_from_codelist)

dataset = create_dataset()
dataset.configure_dummy_data(population_size=500)

start_date = get_parameter("start_date", default="2024-02-01")
index_date = start_date + months(1) - days(1)

'''
This work aims to examine coding patterns within GP consultations related to PF conditions, 
excluding consultations classified as PF consultations. 

For each PF condition, the analysis is restricted to the condition-specific eligible population
based on the relevant PF inclusion and exclusion criteria. 
The base population:
   - alive at the end of the month &
   - registered at the start and end of the month &
   - aged 120 years or under &
   - eligible for the selected PF condition

For each PF condition, consultations are identified using the corresponding PF-condition-specific SNOMED codelists. 
Within these GP consultations, the frequency of each SNOMED code from the same condition-specific codelist is quantified by 
counting the number of unique consultations (consultation_id) in which the code appears.

Detailed approach
1. Use the existing PF-condition-specific SNOMED codelists to identify consultations related to each PF condition (e.g. UTI, sore throat, sinusitis) 
    ---> PF-condition-related consultations
2. Exclude consultations already classified as PF consultations. Restrict the analysis to remaining GP consultations related to the PF condition.
    ---> updated PF-condition-related consultations
3. For each PF condition,
    For each SNOMED code within the same condition-specific codelist, 
        calculate the number of unique consultations (consultation_id) in which the code appears.

The resulting dataset:
- each row representing an individual patient in the condition-specific eligible population
- each column representing the count of a specific SNOMED code
- each cell contains the number of unique non-PF GP consultations in which that code appears for that patient during the month.
'''
#----------------------------------------
# Patient identifiers: alive_status, registration_status, age
alive = patients.is_alive_on(index_date) # alive at the end of month
# Only include the patient if they were registered for the whole month, 
registered_start = practice_registrations.for_patient_on(start_date).exists_for_patient()
registered_index = practice_registrations.for_patient_on(index_date).exists_for_patient()
# Exclude any patients over 120 years old as the date of birth is most likely to be missing
age = patients.age_on(index_date)
age_valid = (patients.age_on(index_date) <= 120) 

base_population = alive & registered_start & registered_index & age_valid 
# dataset.define_population(base_population)

dataset.start_date = case(when(base_population).then(start_date))
dataset.index_date = case(when(base_population).then(index_date))
#----------------------------------------
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
pregnant_this_month_raw = dataset.pregnant.is_in(("P-E", "P-EDD", "P"))
dataset.pregnant_this_month_raw = pregnant_this_month_raw

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
recurrent_impetigo_12m = check_recurrent_status(
    recurrent_impetigo_window_start, 
    recurrent_impetigo_window_end,
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
recurrent_uti_6m = check_recurrent_status(
    recurrent_uti_6m_window_start, 
    recurrent_uti_window_end,
    clinical_events, 
    codelists.gp_snomed_codelist_uti,
    gap_weeks=4, 
    min_episodes=2)
recurrent_uti_12m = check_recurrent_status(
    recurrent_uti_12m_window_start, 
    recurrent_uti_window_end,
    clinical_events, 
    codelists.gp_snomed_codelist_uti,
    gap_weeks=4, 
    min_episodes=3)
recurrent_uti = recurrent_uti_6m | recurrent_uti_12m
dataset.recurrent_uti_6m = recurrent_uti_6m
dataset.recurrent_uti_12m = recurrent_uti_12m
dataset.recurrent_uti = recurrent_uti

#----------------------------------------
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
# exclusion_shingles = pregnant_this_month & (female)
exclusion_shingles = pregnant_this_month_raw & female
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

#----------------------------------------
selected_events = select_events_between(clinical_events, start_date, index_date)

# PF consultation ids
pf_consultation_events = select_events_from_codelist(selected_events, codelists.pf_consultation_events_dict["pf_consultation_services_combined"])
pf_ids = pf_consultation_events.consultation_id

# GP consultation events excluding PF consultations
gp_events_clean = selected_events.where(~selected_events.consultation_id.is_in(pf_ids))

# codelists for PF conditions - long version
pf_gp_codelists = {
    "uti": codelists.gp_snomed_codelist_uti,
    "sinusitis": codelists.gp_snomed_codelist_sinusitis,
    "insectbite": codelists.gp_snomed_codelist_insect_bites,
    "otitismedia": codelists.gp_snomed_codelist_otitis_media,
    "sorethroat": codelists.gp_snomed_codelist_sore_throat,
    "shingles": codelists.gp_snomed_codelist_shingles,
    "impetigo": codelists.gp_snomed_codelist_impetigo,
}

condition = get_parameter("condition", default="sorethroat")
codes = pf_gp_codelists[condition]

for code in codes:

    code_events = gp_events_clean.where(gp_events_clean.snomedct_code == code)

    dataset.add_column(
        f"count_{code}",
        code_events.consultation_id.count_distinct_for_patient(),
    )

#----------------------------------------
eligibility_map = {
    "uti": include_patient_uuti,
    "sinusitis": include_patient_sinusitis,
    "insectbite": include_patient_insect_bites,
    "otitismedia": include_patient_otitis_media,
    "sorethroat": include_patient_sore_throat,
    "shingles": include_patient_shingles,
    "impetigo": include_patient_impetigo,
}
# dataset.define_population(base_population)
dataset.define_population(base_population & eligibility_map[condition])
show(dataset)
