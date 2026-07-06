import pandas as pd

df = pd.read_csv("output/dataset_practices.csv.gz")

df["interval_start"] = pd.to_datetime(df["interval_start"])

summary = (
    df.groupby(["interval_start", "stp"])
    .agg(
        region = ("region", "first"),
        
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

summary.to_csv("output/practice_summary_by_stp.csv", index=False)

print(summary.head())
print(summary.groupby("interval_start")["stp"].nunique())

