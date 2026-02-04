from ehrql.tables.tpp import case, when

"""
Reusable helpers used in dataset definitions.

Functions:
- has_event: checks whether a patient's events contain any code from a codelist
- get_age_band: maps age on specified date to an age-band string
- get_imd: maps IMD (rounded) to a quintile label (1 = most deprived, 5 = least deprived)
- get_latest_ethnicity: computes a single ethnicity value per patient,
  using clinical codes first and falling back to SUS ethnicity if needed.
"""

def has_event(events, codelist):
    return events.where(events.snomedct_code.is_in(codelist)).exists_for_patient()

def get_age_band(patients, index_date):
    age = patients.age_on(index_date)
    age_band = case(
        when((age >= 0) & (age < 20)).then("0-19"),
        when((age >= 20) & (age < 40)).then("20-39"),
        when((age >= 40) & (age < 60)).then("40-59"),
        when((age >= 60) & (age < 80)).then("60-79"),
        when(age >= 80).then("80+"),
        when(age.is_null()).then("Missing"),
    )
    return age_band


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


def get_latest_ethnicity(
    index_date, clinical_events, ethnicity_codelist, ethnicity_from_sus, grouping=6
):
    latest_ethnicity_from_codes_category_num = (
        clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_codelist))
        .where(clinical_events.date.is_on_or_before(index_date))
        .sort_by(clinical_events.date)
        .last_for_patient()
        .snomedct_code.to_category(ethnicity_codelist)
    )

    if grouping == 6:
        latest_ethnicity_from_codes = case(
            when(latest_ethnicity_from_codes_category_num == "1").then("White"),
            when(latest_ethnicity_from_codes_category_num == "2").then("Mixed"),
            when(latest_ethnicity_from_codes_category_num == "3").then(
                "Asian or Asian British"
            ),
            when(latest_ethnicity_from_codes_category_num == "4").then(
                "Black or Black British"
            ),
            when(latest_ethnicity_from_codes_category_num == "5").then(
                "Chinese or Other Ethnic Groups"
            ),
        )

        ethnicity_from_sus = case(
            when(ethnicity_from_sus.code.is_in(["A", "B", "C"])).then("White"),
            when(ethnicity_from_sus.code.is_in(["D", "E", "F", "G"])).then("Mixed"),
            when(ethnicity_from_sus.code.is_in(["H", "J", "K", "L"])).then(
                "Asian or Asian British"
            ),
            when(ethnicity_from_sus.code.is_in(["M", "N", "P"])).then(
                "Black or Black British"
            ),
            when(ethnicity_from_sus.code.is_in(["R", "S"])).then(
                "Chinese or Other Ethnic Groups"
            ),
        )
    elif grouping == 16:
        latest_ethnicity_from_codes = case(
            when(latest_ethnicity_from_codes_category_num == "1").then("White British"),
            when(latest_ethnicity_from_codes_category_num == "2").then("White Irish"),
            when(latest_ethnicity_from_codes_category_num == "3").then("Other White"),
            when(latest_ethnicity_from_codes_category_num == "4").then(
                "White and Caribbean"
            ),
            when(latest_ethnicity_from_codes_category_num == "5").then(
                "White and African"
            ),
            when(latest_ethnicity_from_codes_category_num == "6").then(
                "White and Asian"
            ),
            when(latest_ethnicity_from_codes_category_num == "7").then("Other Mixed"),
            when(latest_ethnicity_from_codes_category_num == "8").then("Indian"),
            when(latest_ethnicity_from_codes_category_num == "9").then("Pakistani"),
            when(latest_ethnicity_from_codes_category_num == "10").then("Bangladeshi"),
            when(latest_ethnicity_from_codes_category_num == "11").then(
                "Other South Asian"
            ),
            when(latest_ethnicity_from_codes_category_num == "12").then("Caribbean"),
            when(latest_ethnicity_from_codes_category_num == "13").then("African"),
            when(latest_ethnicity_from_codes_category_num == "14").then("Other Black"),
            when(latest_ethnicity_from_codes_category_num == "15").then("Chinese"),
            when(latest_ethnicity_from_codes_category_num == "16").then(
                "All other ethnic groups"
            ),
        )

        ethnicity_from_sus = case(
            when(ethnicity_from_sus.code == "A").then("White British"),
            when(ethnicity_from_sus.code == "B").then("White Irish"),
            when(ethnicity_from_sus.code == "C").then("Other White"),
            when(ethnicity_from_sus.code == "D").then("White and Caribbean"),
            when(ethnicity_from_sus.code == "E").then("White and African"),
            when(ethnicity_from_sus.code == "F").then("White and Asian"),
            when(ethnicity_from_sus.code == "G").then("Other Mixed"),
            when(ethnicity_from_sus.code == "H").then("Indian"),
            when(ethnicity_from_sus.code == "J").then("Pakistani"),
            when(ethnicity_from_sus.code == "K").then("Bangladeshi"),
            when(ethnicity_from_sus.code == "L").then("Other South Asian"),
            when(ethnicity_from_sus.code == "M").then("Caribbean"),
            when(ethnicity_from_sus.code == "N").then("African"),
            when(ethnicity_from_sus.code == "P").then("Other Black"),
            when(ethnicity_from_sus.code == "R").then("Chinese"),
            when(ethnicity_from_sus.code == "S").then("All other ethnic groups"),
        )

    ethnicity_combined = case(
        when(latest_ethnicity_from_codes.is_not_null()).then(
            latest_ethnicity_from_codes
        ),
        when(
            latest_ethnicity_from_codes.is_null() & ethnicity_from_sus.is_not_null()
        ).then(ethnicity_from_sus),
        otherwise="Missing",
    )

    return ethnicity_combined