from ehrql import codelist_from_csv

 ####################################################
# SNOMED UK ethnicity category codelist - latest version 22911876
ethnicity_group6_codelist = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="code",
    category_column="Grouping_6",
)
ethnicity_group16_codelist = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="code",
    category_column="Grouping_16",
)

# consultation type -- pending update
gp_codelist_consultation_f2f = codelist_from_csv(
    "codelists/pharmacy-first-project-face-to-face-consultation-codes-for-pharmacy-first.csv",
    column="code"
)
gp_codelist_consultation_online = codelist_from_csv(
    "codelists/pharmacy-first-project-online-consultation-codes-for-pharmacy-first.csv",
    column="code"
)
gp_codelist_consultation_telephone = codelist_from_csv(
    "codelists/pharmacy-first-project-telephone-consultation-codes-for-pharmacy-first.csv",
    column="code"
)

gp_codelist_consultation_econsultation = ["1068881000000101"]

#PF conditions snomed codes used within PF
tx_codelist_pf_otitis_media = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-acute-otitis-media-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_impetigo = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-impetigo-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_infected_insect_bites = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-infected-insect-bites-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_shingles = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-shingles-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_sinusitis = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-sinusitis-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_sore_throat = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-sore-throat-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_urinary_tract_infection = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-urinary-tract-infection-treatment-full-dmd-codelist.csv",
    column="code",
)

####################################################
#Snomed codes used for PF conditions by GPs
gp_snomed_codelist_uti = codelist_from_csv(
    # "codelists/pharmacy-first-project-urinary-tract-infection-and-related-conditions.csv",
    "codelists/pharmacy-first-project-urinary-tract-infection-and-related-conditions-for-pharamcy-first-clone.csv",
    column="code",
)  
gp_snomed_codelist_impetigo = codelist_from_csv(
    "codelists/pharmacy-first-project-impetigo-related-conditions-administration-codes-for-pharmacy-first.csv",
    column="code",
) 
gp_snomed_codelist_otitis_media = codelist_from_csv(
    "codelists/pharmacy-first-project-otitis-media-and-related-conditions.csv",
    column="code",
) 
gp_snomed_codelist_sinusitis = codelist_from_csv(
    "codelists/pharmacy-first-project-sinusitis-related-conditions-administration-codes-for-pharmacy-first.csv",
    column="code",
) 
gp_snomed_codelist_sore_throat = codelist_from_csv(
    "codelists/pharmacy-first-project-Sore-throat-and-related-conditions.csv",
    column="code",
) 
gp_snomed_codelist_insect_bites = codelist_from_csv(
    "codelists/pharmacy-first-project-insect-bites-and-related-conditions-administration-codes-for-pharmacy-first.csv",
    column="code",
) 
gp_snomed_codelist_shingles = codelist_from_csv(
    "codelists/pharmacy-first-project-shingles-and-related-conditions-for-pharmacy-first.csv",
    column="code",
)
####################################################
#Snomed codes used for deciding which one to use for insect bites

gp_snomed_codelist_insect_bites_strict = codelist_from_csv(
    "codelists/pharmacy-first-project-infected-insect-bites-codes-for-pharmacy-first-strict-definition.csv",
    column="code",
) 

gp_snomed_codelist_insect_bites_all = codelist_from_csv(
    "codelists/pharmacy-first-project-all-insect-bites-codes-for-pharmacy-first.csv",
    column="code",
) 

gp_snomed_codelist_cellulitis_only = codelist_from_csv(
    "codelists/pharmacy-first-project-cellulitis-using-snomed-ct-codes.csv",
    column="code",
) 

####################################################
#Snomed codes used for control conditions by GPs
gp_snomed_codelist_lower_back_pain = codelist_from_csv(
    "codelists/pharmacy-first-project-lower-back-pain-for-pf-control.csv",
    column="code",
)


####################################################
#Snomed codes used for specific conditions by GPs - population exclusion criteria
gp_snomed_codelist_urinary_catheter = codelist_from_csv(
    "codelists/pharmacy-first-project-urinary-catheter-administration-codes-for-pharmacy-first.csv",
    column="code",
)

#Snomed codes used for specific conditions by GPs - population exclusion criteria
gp_snomed_codelist_bullous_impetigo = codelist_from_csv(
    "codelists/pharmacy-first-project-bullous-impetigo-administration-codes-for-pharmacy-first.csv",
    column="code",
)

#Snomed codes used for specific conditions by GPs - population exclusion criteria
#current version: pregnancy code by NHSD
gp_snomed_codelist_pregnancy = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-preg_cod.csv",
    column="code",
    category_column="term",
)

# Import no-longer-pregnant codelist
gp_snomed_codelist_end_pregnancy = codelist_from_csv(
    "codelists/pharmacy-first-project-end-of-pregnancy-narrow.csv",
    column="code",
    category_column="term",
)

# estimated date of delivery
gp_snomed_codelist_pregnancy_edd = codelist_from_csv (
    "codelists/user-VickiPalin-pregnancy_edd_snomed.csv"
    , column = "code"
)
####################################################
"""
pf_med_codelist = (
    acute_otitis_media_tx_codelist
    + impetigo_treatment_tx_codelist
    + infected_insect_bites_tx_codelist
    + shingles_treatment_tx_codelist
    + sinusitis_tx_codelist
    + sore_throat_tx_codelist
    + urinary_tract_infection_tx_codelist
)
"""

# Community Pharmacist Consultation Service for minor illness
pf_consultation_cp_minorillness = ["1577041000000109"]
# Pharmacy First service
pf_consultation_service = ["983341000000102"]
# Community Pharmacy First Service
pf_consultation_cp_service = ["2129921000000100"]
 
pf_consultation_events_dict = {
    "pf_consultation_cp_minorillness": pf_consultation_cp_minorillness, # Community Pharmacist (CP) Consultation Service for minor illness (procedure)
    "pf_consultation_service": pf_consultation_service, # Pharmacy First service (qualifier value)
    "pf_consultation_cp_service": pf_consultation_cp_service, # Community Pharmacy Pharmacy First Service
    "pf_consultation_services_combined": pf_consultation_cp_minorillness + pf_consultation_service + pf_consultation_cp_service,
    # "pf_consultation_services_combined": pf_consultation_service + pf_consultation_cp_service,
}
 
uti_code = ["1090711000000102"]
sinusitis_code = ["15805002"]
insectbite_code = ["262550002"]
otitismedia_code = ["3110003"]
sorethroat_code = ["363746003"]
shingles_code = ["4740000"]
impetigo_code = ["48277006"]