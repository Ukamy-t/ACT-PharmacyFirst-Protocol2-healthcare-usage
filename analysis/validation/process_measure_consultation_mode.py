import pandas as pd
import matplotlib.pyplot as plt

input_file = "output/patient_measures_consultation_mode_june.csv"
output_file = "output/patient_measures_consultation_mode_ordered_june.csv"

df = pd.read_csv(input_file)

########################################################
# Define conditions and modes
########################################################

conditions = [
    "uti",
    "sinusitis",
    "insectbite",
    "otitismedia",
    "sorethroat",
    "shingles",
    "impetigo",
]

modes = [
    "f2f",
    "online",
    "telephone",
    "othermode",
]

# Re-order the output csv
measure_order = []
for mode in modes:
    measure_order.append(f"gp_pf_consultation_{mode}")

for condition in conditions:
    measure_order.append(f"gp_consultation_{condition}_total")

    for mode in modes:
        measure_order.append(f"gp_consultation_{condition}_{mode}")

df["measure_order"] = df["measure"].apply(
    lambda x: measure_order.index(x)
    if x in measure_order
    else 999
    )
df = df.sort_values(
    by=[
        "interval_start",
        "measure_order",
        "measure",
    ]
)
df = df.drop(columns=["measure_order"])
df.to_csv(output_file, index=False)


def get_value(month_df, measure_name, column="numerator"):
    result = month_df.loc[month_df["measure"] == measure_name,column]
    if len(result) == 0:
        return None
    return result.iloc[0]

########################################################
# Create summary table
########################################################

summary_rows = []
months = sorted(df["interval_start"].unique())

for month in months:
    month_df = df[df["interval_start"] == month]
    overall_mode_counts = {}

    for mode in modes:
        overall_mode_counts[mode] = get_value(month_df,f"gp_pf_consultation_{mode}")

    # condition-level summary
    for condition in conditions:
        total = get_value(month_df,f"gp_consultation_{condition}_total")
        mode_values = {}

        for mode in modes:
            mode_values[mode] = get_value(month_df,f"gp_consultation_{condition}_{mode}")

        mode_sum = sum(v for v in mode_values.values() if pd.notna(v))

        summary_rows.append({
            "month": month,
            "condition": condition,
            "gp_consultation_total": total,
            "f2f": mode_values["f2f"],
            "online": mode_values["online"],
            "telephone": mode_values["telephone"],
            "othermode": mode_values["othermode"],
            "mode_sum": mode_sum,
            "mode_sum_matches_total": (mode_sum == total
                if pd.notna(total)
                else None
            ),

            "overall_gp_pf_f2f": overall_mode_counts["f2f"],
            "overall_gp_pf_online": overall_mode_counts["online"],
            "overall_gp_pf_telephone": overall_mode_counts["telephone"],
            "overall_gp_pf_othermode": overall_mode_counts["othermode"],
        })

summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(
    "output/patient_measures_consultation_mode_summary_june.csv",
    index=False,
)

########################################################
# Plot overall GP PF consultation counts by mode
########################################################
overall_mode_measures = [
    "gp_pf_consultation_f2f",
    "gp_pf_consultation_online",
    "gp_pf_consultation_telephone",
    "gp_pf_consultation_othermode",
]

plot_df = df[df["measure"].isin(overall_mode_measures)].copy()
plot_df["mode"] = (plot_df["measure"].str.replace("gp_pf_consultation_", "", regex=False))
plot_df["month"] = pd.to_datetime(plot_df["interval_start"]).dt.strftime("%Y-%m")
plot_pivot = plot_df.pivot(
    index="mode",
    columns="month",
    values="numerator",
)

ax = plot_pivot.plot(kind="bar",figsize=(8, 6),)
ax.set_ylabel("GP PF consultation count")
ax.set_xlabel("Consultation mode")
ax.set_title("GP PF consultation count by mode and month")

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("output/patient_measures_gp_pf_consultation_by_mode_june.png",dpi=300,)
plt.close()