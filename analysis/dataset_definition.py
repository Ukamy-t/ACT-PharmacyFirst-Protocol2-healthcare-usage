from ehrql import create_dataset
from ehrql.tables.tpp import patients, practice_registrations, clinical_events
import codelist
dataset = create_dataset()

start_date = "2024-01-31"

index_date = "2025-11-30"
registration_start = practice_registrations.for_patient_on(start_date)
registration_end = practice_registrations.for_patient_on(index_date)
selected_events = clinical_events.where(
    clinical_events.date.is_on_or_between(start_date, index_date)
)
pf_consultation_events = selected_events.where(selected_events.snomedct_code.is_in(codelist.pf_consultation_events_dict["pf_consultation_services_combined"]))

 
dataset.has_pf_consultation = pf_consultation_events.exists_for_patient()
 
pf_ids = pf_consultation_events.consultation_id
selected_pf_id_events = selected_events.where(
    selected_events.consultation_id.is_in(pf_ids)
)
dataset.sex = patients.sex
dataset.age = patients.age_on(index_date)
dataset.define_population(
    registration_start.exists_for_patient() | registration_end.exists_for_patient()) 
