/*
A test version
*/

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
log using "output/PF_WP2_P2_obj1_totals.log", replace

cd "$projectdir"
import delimited "output/dataset_patients_combined.csv", clear
save "output/PF WP2 P2 dummy patient raw data updates Aug26.dta", replace



tab pf_cons_general 
*Consultations are counted by identifying events with these codes and calculating the number of distinct consultation IDs. Multiple condition-specific PF codes recorded within the same consultation are counted as a single consultation.


*generate index_date_stata = date(index_date, "DMY")
gen index_date_stata = date(index_date, "YMD")
format index_date_stata %td
list index_date index_date_stata in 1/10
count if !missing(index_date_stata)
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

**********************************************************
***One-way comparison: total PF consultations by condition
**********************************************************
preserve

* Exclude the overall total variable from reshape
rename num_pf_cons_all total_pf_cons
gen long row_id = _n

* Convert condition-specific variables from wide to long
reshape long num_pf_cons_, i(row_id) j(condition) string
rename num_pf_cons_ num_pf_cons

tabstat num_pf_cons, by(condition) statistics(sum)

restore

* Total PF consultations by date
tabstat num_pf_cons_all, by(index_date_stata) statistics(sum)

* Total PF consultations by region
tabstat num_pf_cons_all, by(region) statistics(sum)

* Total PF consultations by STP
* tabstat num_pf_cons_all, by(stp) statistics(sum)

* Total PF consultations by age group
tabstat num_pf_cons_all, by(age_group) statistics(sum)

* Total PF consultations by sex
tabstat num_pf_cons_all, by(sex) statistics(sum)

* Total PF consultations by ethnicity
tabstat num_pf_cons_all, by(ethnicity) statistics(sum)

* Total PF consultations by IMD
tabstat num_pf_cons_all, by(imd) statistics(sum)

**********************************************************
***Two way comparisons of number of PF consultations by condition and by...
**********************************************************
preserve

gen long row_id = _n

* Includes num_pf_cons_all as condition = "all"
reshape long num_pf_cons_, i(row_id) j(condition) string
rename num_pf_cons_ num_pf_cons

* Date × condition
table index_date_stata condition, contents(sum num_pf_cons)

* Region × condition
table region condition, contents(sum num_pf_cons)

* STP × condition
* table stp condition, contents(sum num_pf_cons)

* Age group × condition
table age_group condition, contents(sum num_pf_cons)

* Sex × condition
table sex condition, contents(sum num_pf_cons)

* Ethnicity × condition
table ethnicity condition, contents(sum num_pf_cons)

* IMD × condition
table imd condition, contents(sum num_pf_cons)

restore

**********************************************************
*** Three-way comparisons
**********************************************************

**************************************************
* Consultation counts by condition, date and subgroup
**************************************************
preserve

gen long row_id = _n

* Convert condition-specific consultation counts to long format
* num_pf_cons_all will appear as condition = "all"
reshape long num_pf_cons_, i(row_id) j(condition) string
rename num_pf_cons_ num_pf_cons

* Condition × date, subgrouped by region
table condition index_date_stata region, ///
    contents(sum num_pf_cons)

* Condition × date, subgrouped by STP
table condition index_date_stata stp, ///
    contents(sum num_pf_cons)

* Condition × date, subgrouped by age group
table condition index_date_stata age_group, ///
    contents(sum num_pf_cons)

* Condition × date, subgrouped by sex
table condition index_date_stata sex, ///
    contents(sum num_pf_cons)

* Condition × date, subgrouped by ethnicity
table condition index_date_stata ethnicity, ///
    contents(sum num_pf_cons)

* Condition × date, subgrouped by IMD
table condition index_date_stata imd, ///
    contents(sum num_pf_cons)

restore


**************************************************
* Eligible population by condition, date and subgroup
**************************************************
preserve

gen long row_id = _n

* Convert condition-specific eligibility indicators to long format
reshape long inc_pt_, i(row_id) j(condition) string
rename inc_pt_ eligible_patients

* Condition × date, subgrouped by region
table condition index_date_stata region, ///
    contents(sum eligible_patients)

* Condition × date, subgrouped by STP
table condition index_date_stata stp, ///
    contents(sum eligible_patients)

* Condition × date, subgrouped by age group
table condition index_date_stata age_group, ///
    contents(sum eligible_patients)

* Condition × date, subgrouped by sex
table condition index_date_stata sex, ///
    contents(sum eligible_patients)

* Condition × date, subgrouped by ethnicity
table condition index_date_stata ethnicity, ///
    contents(sum eligible_patients)

* Condition × date, subgrouped by IMD
table condition index_date_stata imd, ///
    contents(sum eligible_patients)

restore


**************************************************
* Close totals log and open rates log
**************************************************
capture log close
log using "output/PF_WP2_P2_obj1_rates.log", text replace


**********************************************************
*** Rates by practice and patient characteristics
**********************************************************

* Variables that need to be summed before calculating rates
local collapse_vars ///
    num_pf_cons_uti ///
    num_pf_cons_sinusitis ///
    num_pf_cons_ibite ///
    num_pf_cons_otitismedia ///
    num_pf_cons_sorethroat ///
    num_pf_cons_shingles ///
    num_pf_cons_impetigo ///
    inc_pt_otitis_media ///
    inc_pt_sinusitis ///
    inc_pt_sore_throat ///
    inc_pt_insect_bites ///
    inc_pt_shingles ///
    inc_pt_impetigo ///
    inc_pt_uuti


* Run the same analysis for each subgroup
foreach subgroup in region stp age_group sex ethnicity imd {

    preserve

    * Obtain totals for each practice, month and subgroup
    collapse (sum) `collapse_vars', ///
        by(index_date_stata practice `subgroup')

    * Rates per 100 eligible patients
    gen rate_pf_cons_uti = ///
        100 * num_pf_cons_uti / inc_pt_uuti ///
        if inc_pt_uuti > 0

    gen rate_pf_cons_sinusitis = ///
        100 * num_pf_cons_sinusitis / inc_pt_sinusitis ///
        if inc_pt_sinusitis > 0

    gen rate_pf_cons_ibite = ///
        100 * num_pf_cons_ibite / inc_pt_insect_bites ///
        if inc_pt_insect_bites > 0

    gen rate_pf_cons_otitismedia = ///
        100 * num_pf_cons_otitismedia / inc_pt_otitis_media ///
        if inc_pt_otitis_media > 0

    gen rate_pf_cons_sorethroat = ///
        100 * num_pf_cons_sorethroat / inc_pt_sore_throat ///
        if inc_pt_sore_throat > 0

    gen rate_pf_cons_shingles = ///
        100 * num_pf_cons_shingles / inc_pt_shingles ///
        if inc_pt_shingles > 0

    gen rate_pf_cons_impetigo = ///
        100 * num_pf_cons_impetigo / inc_pt_impetigo ///
        if inc_pt_impetigo > 0

    * Convert condition-specific rates to long format
    gen long rate_row_id = _n

    reshape long rate_pf_cons_, ///
        i(rate_row_id) j(condition) string

    rename rate_pf_cons_ rate_pf_cons

    * Mean practice-level rate by condition, date and subgroup
    table condition index_date_stata `subgroup', ///
        contents(mean rate_pf_cons)

    restore
}


**************************************************
* Close log
**************************************************
log close 