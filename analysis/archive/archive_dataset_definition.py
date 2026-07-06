    #this file defines the population and selects the fields that need to be included in the data for 
    # analysis. 
        
from ehrql import create_dataset, show
from ehrql.tables.tpp import (
    patients, 
    practice_registrations, 
    clinical_events,
    addresses,
    case,
    when
)
import codelists

dataset = create_dataset()

dataset.configure_dummy_data(population_size=1000)
    # for start to end of whole period
#start_date = "2024-01-31"
#index_date = "2026-01-31"

    # One month time period (to start with this is Nov 25) 
start_date = "2025-10-31"     
index_date = "2025-11-30"        

    ##The criteria for objective 1 are as follows:
    # patient alive and registered with the practice on the index date
    #include only patients who are registered and PF clinical events between the index and start date
registration_start = practice_registrations.for_patient_on(start_date)
registration_end = practice_registrations.for_patient_on(index_date)
selected_events = clinical_events.where(
    clinical_events.date.is_on_or_between(start_date, index_date)
)
pf_consultation_events = selected_events.where(selected_events.snomedct_code.is_in(codelists.pf_consultation_events_dict["pf_consultation_services_combined"]))

#include if pt is alive
dataset.alive= patients.is_alive_on(index_date)   

    # exclude practices which are unusual (e.g very small practices, so from practice list size)
    #do this using practice file (need practice size)


    #Denominator criteria create the fields ready to combine below:
    #first create fields for:
        #add patients sex 
dataset.sex = patients.sex

        #add patient age
dataset.age = patients.age_on(index_date)
       
        #pregnancy-rule? pregnant and no_longer_pregnant codes, full term pregnancy end code, shortened pregnancy end code
            #patient_pregnant
        #catheter-rule? excluding patients who clearly have a catheter, and for following 12 months after code is included
            #patient_has_catheter=
        #recurrent UTI (2 episodes in last 6 months, or 3 episodes in last 12 months) an episode is defined as a 4 week period, so any codes within this time are considered to be part of the same episode.
        #bullous impetigo (within what period?) within 4 weeks following PF consultation?
        #recurrent impetigo (defined as 2 or more episodes in the same year) an episode is defined as a 4 week period, so any codes within this time are considered to be part of the same episode.
    
    #Then create flag for 'eligible' for PF by condition:
            #Urinary tract infection: women aged 16 to 64 years, exclude pregnant individuals, *urinary catheter and recurrent UTI (2 episodes in last 6 months, or 3 episodes in last 12 months)
                #eligible_UTI
            #Shingles: adults aged 18 years and over, exclude pregnant individuals
    	    #Impetigo: adults and children aged 1 year and over, exclude bullous impetigo, recurrent impetigo (defined as 2 or more episodes in the same year), pregnant individuals under 16 years
    	    #Infected insect bites: adults and children aged 1 year and over, exclude pregnant individuals under 16 years
    	    #Acute sore throat: adults and children aged 5 years and over, exclude pregnant individuals under 16 years
    	    #Acute sinusitis: adults and children aged 12 years and over
    	    #Acute Otis media: children aged 1 to 17 years, exclude pregnant individuals under 16 years
     
   
    #Numerators for PF consultations by condition:
        #add if the patient has a PF consultation recorded in the GP data
dataset.has_pf_consultation = pf_consultation_events.exists_for_patient()

        #PF consultation for UTI, Shingles, Impetigo, Infected Insect bites, Acute sore throat, Acute sinusitis, Acute otitis media and check consultation ID matches- creates binary outcome for each condition
pf_ids = pf_consultation_events.consultation_id
selected_pf_id_events = selected_events.where(
    selected_events.consultation_id.is_in(pf_ids)
)
def has_event(events, codelist):
    return events.where(events.snomedct_code.is_in(codelist)).exists_for_patient()
dataset.uti_numerator = has_event(
    selected_pf_id_events,
    codelists.uti_code,
)
dataset.sinusitis_numerator = has_event(
    selected_pf_id_events,
    codelists.sinusitis_code,
)
dataset.insectbite_numerator = has_event(
    selected_pf_id_events,
    codelists.insectbite_code,
)
dataset.otitismedia_numerator = has_event(
    selected_pf_id_events,
    codelists.otitismedia_code,
)
dataset.sorethroat_numerator = has_event(
    selected_pf_id_events,
    codelists.sorethroat_code,
)
dataset.shingles_numerator = has_event(
    selected_pf_id_events,
    codelists.shingles_code,
)
    #Covariates needed
            
        #patient ethnicity
       
        #practice size (from practice define file)

        #age and sex added above to define denominator

        #adds practice ID 
dataset.practice = practice_registrations.for_patient_on(index_date).practice_pseudo_id
'''
        #adds practice STP but currently all empty!
dataset.stp = practice_registrations.for_patient_on(index_date).practice_stp

        #adds practice region but currently all empty!
dataset.region = practice_registrations.for_patient_on(index_date).practice_nuts1_region_name
'''

        #add pt IMD- says missing address file when run
def get_imd(addresses, index_date):
    imd_rounded = addresses.for_patient_on(index_date).imd_rounded
    max_imd = 32844
    imd_quintile = case(
        when((imd_rounded >= 0) & (imd_rounded < int(max_imd * 1 / 5))).then(
            "1 (Most Deprived)"
        ),
        when(imd_rounded < int(max_imd * 2 / 5)).then("2"),
        when(imd_rounded < int(max_imd * 3 / 5)).then("3"),
        when(imd_rounded < int(max_imd * 4 / 5)).then("4"),
        when(imd_rounded <= max_imd).then("5 (Least Deprived)"),
        otherwise="Missing",
    )
    return imd_quintile
 
dataset.imd = get_imd(addresses, index_date)

#dataset.practice_id= patients.practice_pseudo_id


dataset.define_population(patients.exists_for_patient())
registration_start.exists_for_patient() | registration_end.exists_for_patient()
show(dataset)

#for objective 3, we additionally need:
        #consultations for PF related conditions within the GP practice
        #consultation type

#for objective 4, we additionally need:
        #consultations for PF related conditions within the A&E data