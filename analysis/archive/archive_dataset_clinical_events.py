# This file is for debug purpose / WM

from ehrql import show, months, days, create_dataset
from ehrql.tables.tpp import clinical_events, patients
import codelists

index_date = "2025-11-30"

dataset = create_dataset()
dataset.configure_dummy_data(population_size=1000)


impetigo_events = (
    clinical_events
    .where(clinical_events.snomedct_code == "48277006")
    .where(clinical_events.date.is_on_or_between(index_date - months(24), index_date))
)
impetigo_event_count = impetigo_events.count_for_patient()

sore_throat_events = (
    clinical_events
    .where(clinical_events.snomedct_code == "363746003")
    .where(clinical_events.date.is_on_or_between(index_date - months(24), index_date))
)
sore_throat_event_count = sore_throat_events.count_for_patient()

dataset.impetigo_event_count = impetigo_event_count
dataset.sore_throat_event_count = sore_throat_event_count

dataset.age = patients.age_on(index_date)
dataset.define_population(patients.exists_for_patient())

show(dataset)