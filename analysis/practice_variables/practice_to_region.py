import pandas as pd

df = pd.read_csv("output/dataset_practices.csv.gz")

df["interval_start"] = pd.to_datetime(df["interval_start"])

summary_region = (
    df.groupby(["interval_start", "region"])
    .agg(
        n_stp=("stp", "nunique"),
        n_practices=("practice", "nunique"),
        
        population_total=("population", "sum"),
        population_max_practice=("population", "max"),
        population_min_practice=("population", "min"),
        
        appointments_scheduled=("appointments_scheduled", "sum"),
        appointments_seen=("appointments_seen", "sum"),
        
        # pf_consultation_general=("pf_consultation_general", "sum"),
        # pf_consultation_uti=("pf_consultation_uti", "sum"),
        
        # populationeligible_uuti=("populationeligible_uuti", "sum"),
    )
    .reset_index()
)

summary_region.to_csv("output/practice_summary_by_region.csv", index=False)