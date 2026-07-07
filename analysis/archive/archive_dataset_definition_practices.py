#This file defines the practices for the patients and selects the fields that need to be included in the data for analysis. 
#This data includes the denominator of the practice population for objective 2, the numerators will be all consultations 
from analysis.pf_variable_library import get_imd, get_latest_ethnicity, select_events_between, select_events_from_codelist, select_events_by_consultation_id, has_event_count
from ehrql import INTERVAL, case, create_dataset, days, months, when, show
from ehrql.tables.tpp import addresses, ethnicity_from_sus, patients, practice_registrations, clinical_events, appointments

import codelists

from ehrql import claim_permissions
claim_permissions("appointments")

dataset = create_dataset()
dataset.configure_dummy_data(population_size=500)

# One month time period
start_date = INTERVAL.start_date    
index_date = INTERVAL.end_date
# start_date = "2024-02-01"  
# index_date = start_date + months(1) - days(1)

sex = patients.sex
age = patients.age_on(index_date)
age_valid = (patients.age_on(index_date) <= 120) # "Exclude any patients over 120 years old as the date of birth is most likely to be missing"
alive = patients.is_alive_on(index_date) # alive at the end of month
registered_start = practice_registrations.for_patient_on(start_date).exists_for_patient()
registered_index = practice_registrations.for_patient_on(index_date).exists_for_patient()

dataset.start_date = start_date
dataset.index_date = index_date
dataset.define_population(patients.exists_for_patient())
dataset.registered_start = registered_start
dataset.registered_index = registered_index
dataset.alive = alive
dataset.sex = sex
dataset.age = age
dataset.imd = get_imd(addresses, index_date)
dataset.ethnicity = get_latest_ethnicity(index_date,clinical_events,codelists.ethnicity_group16_codelist,ethnicity_from_sus,grouping=16,)

dataset.practice = practice_registrations.for_patient_on(index_date).practice_pseudo_id
dataset.stp = practice_registrations.for_patient_on(index_date).practice_stp
dataset.region = case(
    when(practice_registrations.for_patient_on(index_date).practice_nuts1_region_name.is_null()).then("Missing"),
    otherwise=practice_registrations.for_patient_on(index_date).practice_nuts1_region_name,
)

selected_events = clinical_events.where(
    clinical_events.date.is_on_or_between(start_date, index_date)
)
pf_consultation_events = selected_events.where(selected_events.snomedct_code.is_in(codelists.pf_consultation_events_dict["pf_consultation_services_combined"]))

########################################################
# PF consultation count for each condition
selected_events = select_events_between(clinical_events, start_date, index_date)
pf_consultation_events = select_events_from_codelist(selected_events, codelists.pf_consultation_events_dict["pf_consultation_services_combined"])
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

for name, codes in pf_conditions_pf_codes.items():
    # count for patient OR count for episode?
    # count events, consultations or episodes?
    count_pf_event, count_pf_consultation, count_pf_episode = has_event_count(selected_pf_id_events, codes)
    setattr(dataset, f"numerator_pf_event_{name}", count_pf_event)
    setattr(dataset, f"numerator_pf_consultation_{name}", count_pf_consultation)
    setattr(dataset, f"numerator_pf_episode_{name}", count_pf_episode)

# a set of codes for any PF condition
pf_conditions_pf_code_set = (
    codelists.uti_code
    + codelists.sinusitis_code
    + codelists.insectbite_code
    + codelists.otitismedia_code
    + codelists.sorethroat_code
    + codelists.shingles_code
    + codelists.impetigo_code
)
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

########################################################
# Total appointments attended in the period
appointment_events = appointments.where(
    (appointments.seen_date.is_on_or_between(start_date, index_date)) &
    (appointments.status.is_in([
            "Arrived",
            "In Progress",
            "Finished",
            "Visit",
            "Patient Walked Out",
            "Did Not Attend"
        ]))
    # (appointments.status == "Arrived")
)
# count attended appointments per patient
dataset.appointment_count = appointment_events.count_for_patient()

########################################################
# Total consultations by consultation type (only count face-to-face, telephone)





show(dataset)