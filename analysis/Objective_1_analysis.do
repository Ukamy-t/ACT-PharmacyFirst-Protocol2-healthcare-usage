/*==============================================================================
DO FILE NAME:			PF_WP2_obj1_Jul26
PROJECT:				Pharmacy First WP2
AUTHOR:					A Taylor							
DESCRIPTION OF FILE:	analysis for Objective 1
DATASETS USED:			output/pf_consultations_by_month.csv
OUTPUT: 		    	logfiles, printed to folder $Logdir
					
==============================================================================*/

*Set filepaths
global projectdir `c(pwd)'
di "$projectdir"

/*
capture mkdir "$projectdir/output/data"
capture mkdir "$projectdir/output/tables"
capture mkdir "$projectdir/output/figures"
*/

global logdir "$projectdir/logs"
di "$logdir"

*Open a log file
cap log close
log using "outputs/PF_WP2_P2_obj1_totals.log" replace

cd "$projectdir"
import delimited "output/dataset_patients_combined.csv", clear
save "output/PF WP2 P2 dummy patient raw data updates Aug26.dta", replace



tab pf_cons_general 
*Consultations are counted by identifying events with these codes and calculating the number of distinct consultation IDs. Multiple condition-specific PF codes recorded within the same consultation are counted as a single consultation.


generate index_date_stata = date(index_date, "DMY")
format index_date_stata %td
*create variable for all PF conditions added together (consultation level)
gen num_pf_cons_all=num_pf_cons_uti +num_pf_cons_sinusitis +num_pf_cons_ibite +num_pf_cons_otitismedia +num_pf_cons_sorethroat +num_pf_cons_shingles +num_pf_cons_impetigo

gen age_group=""
replace age_group= "0 to 19" if age>=0 & age<=19 
replace age_group= "20 to 39" if age>=20 & age<=39 
replace age_group= "40 to 59" if age>=40 & age<=59 
replace age_group= "60 to 79" if age>=60 & age<=79 
replace age_group= "80 and over" if age>=80

set linesize 255


replace inc_pt_otitis_media="1" if inc_pt_otitis_media=="T"
replace inc_pt_otitis_media="0" if inc_pt_otitis_media=="F"

replace inc_pt_sinusitis="1" if inc_pt_sinusitis =="T"
replace inc_pt_sinusitis="0" if inc_pt_sinusitis =="F"

replace inc_pt_sore_throat="1" if inc_pt_sore_throat =="T"
replace inc_pt_sore_throat="0" if inc_pt_sore_throat =="F"

replace inc_pt_insect_bites="1" if inc_pt_insect_bites =="T"
replace inc_pt_insect_bites="0" if inc_pt_insect_bites =="F"

replace inc_pt_shingles="1" if inc_pt_shingles =="T"
replace inc_pt_shingles="0" if inc_pt_shingles =="F"

replace inc_pt_impetigo="1" if inc_pt_impetigo =="T"
replace inc_pt_impetigo="0" if inc_pt_impetigo =="F"

replace inc_pt_uuti="1" if inc_pt_uuti =="T"
replace inc_pt_uuti="0" if inc_pt_uuti =="F"

replace inc_pt_all_eligible="1" if inc_pt_all_eligible =="T"
replace inc_pt_all_eligible="0" if inc_pt_all_eligible =="F"

destring inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible, replace    


set more off


log using "outputs/PF_WP2_P2_obj1_totals.log", text replace

**One way comparisons number of PF consultations by...
*condition (row)
table, statistic(sum num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo) 

*date (row)
table (index_date), command(total num_pf_cons_all)

*region
table (region), command(total num_pf_cons_all)

*stp
*table (stp), command(total num_pf_cons_all)

*age_group
table (age_group), command(total num_pf_cons_all)

*sex
table (sex), command(total num_pf_cons_all)

*ethnicity
table (ethnicity), command(total num_pf_cons_all)

*imd
table (imd), command(total num_pf_cons_all)


***Two way comparisons of number of PF consultations by condition and by...
*date-table of number of consultations by PF condition (column) by date (row)
table (index_date), command(total num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all) 


table (index_date), command(total inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible)
/*
*region
*table (var) (region), stat(total num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo)
table (region), command(total num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all)

table (region), command(total inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible)

*stp
*table (stp), command(total num_pf_cons_all)

*age_group
table (age_group), command(total num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all)

table (age_group), command(total inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible)

*sex
table (sex), command(total num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all)

table (sex), command(total inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible)

*ethnicity
table(ethnicity), command(total num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all)

table(ethnicity), command(total inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible)

*imd
table (imd), command(total num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all)			
		
table (imd), command (total inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible)		
		*/				
/*						
***Three way comparisons
*table of number of consultations by PF condition (row) by region (subgrouped) and date (columns)
table (region) (index_date), command (total num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all)

table  (region)(index_date), command (total inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible)

*table of number of consultations by PF condition (row) by stp (subgrouped) and date (columns)
table (stp) (index_date), command (total num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all)

table  (stp)(index_date), command (total inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible)

*table of number of consultations by PF condition (row) by age_group (subgrouped) and date (columns)
table (age_group) (index_date), command (total num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all)

table  (age_group)(index_date), command (total inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible)

*table of number of consultations by PF condition (row) by sex (subgrouped) and date (columns)
table (sex) (index_date), command (total num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all)

table  (sex)(index_date), command (total inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible)

*table of number of consultations by PF condition (row) by ethnicity (subgrouped) and date (columns)
table (ethnicity) (index_date), command (total num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all)

table  (ethnicity)(index_date), command (total inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible)

*table of number of consultations by PF condition (row) by imd (subgrouped) and date (columns)
table (imd) (index_date), command (total num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all)

table (imd)(index_date), command (total inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible)
log close


****************************************
****************************************
****************************************
*Calculating rates by practice and patient characteristics
log using "PF_WP2_P2_obj1_rates.log", text replace

preserve
**tab rate of consultations by practice level variables

collapse (count) num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all  inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible , by (index_date practice region stp)

gen rate_pf_cons_uti =num_pf_cons_uti/ inc_pt_uuti *100
gen rate_pf_cons_sorethroat =num_pf_cons_sorethroat/inc_pt_sore_throat *100
gen rate_pf_cons_sinusitis =num_pf_cons_sinusitis/ inc_pt_sinusitis  *100
gen rate_pf_cons_shingles =num_pf_cons_shingles/ inc_pt_shingles *100
gen rate_pf_cons_otitismedia =num_pf_cons_otitismedia/ inc_pt_otitis_media *100
gen rate_pf_cons_impetigo =num_pf_cons_impetigo/ inc_pt_impetigo *100
gen rate_pf_cons_ibite_all =num_pf_cons_ibite/inc_pt_insect_bites*100


///recode region_East region_East_Midlands region_London region_Missing region_North_East region_South_East region_South_West region_West_Midlands region_York_and_Humber (missing = 0) , prefix(new_)

*table of number of consultations by PF condition (row) by region (subgrouped) and date (columns)
table (region) (index_date), command (mean rate_pf_cons_uti rate_pf_cons_sorethroat rate_pf_cons_sinusitis rate_pf_cons_shingles rate_pf_cons_otitismedia rate_pf_cons_impetigo rate_pf_cons_ibite_all)

restore
***************************
**age
preserve

**tab rate of consultations by patient level variables
collapse (count) num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible , by (index_date practice age_group)

gen rate_pf_cons_uti =num_pf_cons_uti/ inc_pt_uuti *100
gen rate_pf_cons_sorethroat =num_pf_cons_sorethroat/inc_pt_sore_throat *100
gen rate_pf_cons_sinusitis =num_pf_cons_sinusitis/ inc_pt_sinusitis  *100
gen rate_pf_cons_shingles =num_pf_cons_shingles/ inc_pt_shingles *100
gen rate_pf_cons_otitismedia =num_pf_cons_otitismedia/ inc_pt_otitis_media *100
gen rate_pf_cons_impetigo =num_pf_cons_impetigo/ inc_pt_impetigo *100
gen rate_pf_cons_ibite_all =num_pf_cons_ibite/inc_pt_insect_bites*100

table (age_group) (index_date), command (mean rate_pf_cons_uti rate_pf_cons_sorethroat rate_pf_cons_sinusitis rate_pf_cons_shingles rate_pf_cons_otitismedia rate_pf_cons_impetigo rate_pf_cons_ibite_all)

restore

**sex
preserve
**tab rate of consultations by patient level variables
collapse (count) num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible , by (index_date practice sex)

gen rate_pf_cons_uti =num_pf_cons_uti/ inc_pt_uuti *100
gen rate_pf_cons_sorethroat =num_pf_cons_sorethroat/inc_pt_sore_throat *100
gen rate_pf_cons_sinusitis =num_pf_cons_sinusitis/ inc_pt_sinusitis  *100
gen rate_pf_cons_shingles =num_pf_cons_shingles/ inc_pt_shingles *100
gen rate_pf_cons_otitismedia =num_pf_cons_otitismedia/ inc_pt_otitis_media *100
gen rate_pf_cons_impetigo =num_pf_cons_impetigo/ inc_pt_impetigo *100
gen rate_pf_cons_ibite_all =num_pf_cons_ibite/inc_pt_insect_bites*100

table (sex) (index_date), command (mean rate_pf_cons_uti rate_pf_cons_sorethroat rate_pf_cons_sinusitis rate_pf_cons_shingles rate_pf_cons_otitismedia rate_pf_cons_impetigo rate_pf_cons_ibite_all)

restore

**ethnicity
preserve
collapse (count) num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible , by (index_date practice ethnicity)

gen rate_pf_cons_uti =num_pf_cons_uti/ inc_pt_uuti *100
gen rate_pf_cons_sorethroat =num_pf_cons_sorethroat/inc_pt_sore_throat *100
gen rate_pf_cons_sinusitis =num_pf_cons_sinusitis/ inc_pt_sinusitis  *100
gen rate_pf_cons_shingles =num_pf_cons_shingles/ inc_pt_shingles *100
gen rate_pf_cons_otitismedia =num_pf_cons_otitismedia/ inc_pt_otitis_media *100
gen rate_pf_cons_impetigo =num_pf_cons_impetigo/ inc_pt_impetigo *100
gen rate_pf_cons_ibite_all =num_pf_cons_ibite/inc_pt_insect_bites*100

*table of number of consultations by PF condition (row) by ethnicity (subgrouped) and date (columns)
table (ethnicity) (index_date), command (mean rate_pf_cons_uti rate_pf_cons_sorethroat rate_pf_cons_sinusitis rate_pf_cons_shingles rate_pf_cons_otitismedia rate_pf_cons_impetigo rate_pf_cons_ibite_all)

restore

**imd
preserve
collapse (count) num_pf_cons_uti num_pf_cons_sinusitis num_pf_cons_ibite num_pf_cons_otitismedia num_pf_cons_sorethroat num_pf_cons_shingles num_pf_cons_impetigo num_pf_cons_all inc_pt_otitis_media inc_pt_sinusitis inc_pt_sore_throat inc_pt_insect_bites inc_pt_shingles inc_pt_impetigo inc_pt_uuti inc_pt_all_eligible , by (index_date practice imd)

gen rate_pf_cons_uti =num_pf_cons_uti/ inc_pt_uuti *100
gen rate_pf_cons_sorethroat =num_pf_cons_sorethroat/inc_pt_sore_throat *100
gen rate_pf_cons_sinusitis =num_pf_cons_sinusitis/ inc_pt_sinusitis  *100
gen rate_pf_cons_shingles =num_pf_cons_shingles/ inc_pt_shingles *100
gen rate_pf_cons_otitismedia =num_pf_cons_otitismedia/ inc_pt_otitis_media *100
gen rate_pf_cons_impetigo =num_pf_cons_impetigo/ inc_pt_impetigo *100
gen rate_pf_cons_ibite_all =num_pf_cons_ibite/inc_pt_insect_bites*100


*table of number of consultations by PF condition (row) by imd (subgrouped) and date (columns)
table (imd) (index_date), command (mean rate_pf_cons_uti rate_pf_cons_sorethroat rate_pf_cons_sinusitis rate_pf_cons_shingles rate_pf_cons_otitismedia rate_pf_cons_impetigo rate_pf_cons_ibite_all)

restore
*/
log close 






// read arrow output from ehrql
// stata itself does not directly support .arrow. However, OpenSAFELY's Stata Docker
// image contains the arrowload library that can load .arrow files in Stata.

//. arrowload /path/to/arrow/file

// read compressed CSV output from ehrql
// stata cannot handle compressed CSV files directly, so unzip first to a plain CSV file
// the unzipped file will be discarded when the action finishes.
!gunzip output/dataset.csv.gz

// now import the uncompressed CSV using delimited
import delimited using output/dataset.csv

// save in compressed dta.gz format
gzsave output/model.dta.gz

// load a compressed .dta.gz file
gzload output/dataset.dta.gz

INPUT_FILE = "./output/dataset_patients_combined.csv.gz"

// Load the input dataset generated by OpenSAFELY
*created using dummy data
import delimited "output/dataset_patients_combined.csv.gz", clear

// Perform statistical analysis
summarize age
*logistic outcome i.gender age

// Save output results back to the OpenSAFELY output folder
*outreg2 using "output/results .xls", replace