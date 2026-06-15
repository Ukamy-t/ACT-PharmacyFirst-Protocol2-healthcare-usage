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

control_conditions = [
    "lowerbackpain",
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
    measure_order.append(f"gp_pf_patient_date_{mode}")
measure_order.append("gp_pf_patient_date_total")
measure_order.append("gp_pf_patient_date_mode_sum")

# Condition-specific measures
for condition in conditions:
    # Original consultation-ID-based total
    measure_order.append(f"gp_consultation_{condition}_total")

    # New patient-date-based total and validation
    measure_order.append(f"gp_{condition}_patient_date_total")
    measure_order.append(f"gp_{condition}_patient_date_mode_sum")

    for mode in modes:
        measure_order.append(f"gp_{condition}_patient_date_{mode}")

# Control condition-specific measures
for condition in control_conditions:
    measure_order.append(f"gp_consultation_{condition}_total")
    measure_order.append(f"gp_{condition}_patient_date_total")
    measure_order.append(f"gp_{condition}_patient_date_mode_sum")

    for mode in modes:
        measure_order.append(f"gp_{condition}_patient_date_{mode}")

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
        overall_mode_counts[mode] = get_value(month_df,f"gp_pf_patient_date_{mode}")
    overall_total = get_value(month_df, "gp_pf_patient_date_total")
    overall_mode_sum = get_value(month_df, "gp_pf_patient_date_mode_sum")

    # condition-level summary
    for condition in conditions:
        consultation_total = get_value(
            month_df,
            f"gp_consultation_{condition}_total",
        )

        patient_date_total = get_value(
            month_df,
            f"gp_{condition}_patient_date_total",
        )

        patient_date_mode_sum_recorded = get_value(
            month_df,
            f"gp_{condition}_patient_date_mode_sum",
        )

        mode_values = {}

        for mode in modes:
            mode_values[mode] = get_value(month_df,f"gp_{condition}_patient_date_{mode}")

        mode_sum_calculated = sum(v for v in mode_values.values() if pd.notna(v))

        summary_rows.append({
            "month": month,
            "condition": condition,
            
            "gp_consultation_total": consultation_total, # original consultation-ID-based total

            "gp_patient_date_total": patient_date_total, # new patient-date-based total

            "f2f": mode_values["f2f"],
            "online": mode_values["online"],
            "telephone": mode_values["telephone"],
            "othermode": mode_values["othermode"],

            "patient_date_mode_sum_calculated": mode_sum_calculated,
            "patient_date_mode_sum_recorded": patient_date_mode_sum_recorded,

            # Validation checks
            "calculated_mode_sum_matches_patient_date_total": (
                mode_sum_calculated == patient_date_total
                if pd.notna(patient_date_total)
                else None
            ),
            "recorded_mode_sum_matches_patient_date_total": (
                patient_date_mode_sum_recorded == patient_date_total
                if pd.notna(patient_date_total)
                else None
            ),
            "calculated_mode_sum_matches_recorded_mode_sum": (
                mode_sum_calculated == patient_date_mode_sum_recorded
                if pd.notna(patient_date_mode_sum_recorded)
                else None
            ),

            # Overall PF-related GP patient-date counts
            "overall_gp_pf_patient_date_total": overall_total,
            "overall_gp_pf_patient_date_mode_sum": overall_mode_sum,
            "overall_gp_pf_f2f": overall_mode_counts["f2f"],
            "overall_gp_pf_online": overall_mode_counts["online"],
            "overall_gp_pf_telephone": overall_mode_counts["telephone"],
            "overall_gp_pf_othermode": overall_mode_counts["othermode"],
        })

    # Control condition-level summary
    for condition in control_conditions:
        consultation_total = get_value(month_df,f"gp_consultation_{condition}_total",)

        patient_date_total = get_value(month_df,f"gp_{condition}_patient_date_total",)

        patient_date_mode_sum_recorded = get_value(month_df,f"gp_{condition}_patient_date_mode_sum",)

        mode_values = {}
        for mode in modes:
            mode_values[mode] = get_value(month_df,f"gp_{condition}_patient_date_{mode}",)

        mode_sum_calculated = sum(v for v in mode_values.values()if pd.notna(v))

        summary_rows.append({
            "month": month,
            "condition": condition,

            "gp_consultation_total": consultation_total,

            "gp_patient_date_total": patient_date_total,
            "f2f": mode_values["f2f"],
            "online": mode_values["online"],
            "telephone": mode_values["telephone"],
            "othermode": mode_values["othermode"],

            "patient_date_mode_sum_calculated": mode_sum_calculated,
            "patient_date_mode_sum_recorded": patient_date_mode_sum_recorded,

            "calculated_mode_sum_matches_patient_date_total": (
                mode_sum_calculated == patient_date_total
                if pd.notna(patient_date_total)
                else None
            ),
            "recorded_mode_sum_matches_patient_date_total": (
                patient_date_mode_sum_recorded == patient_date_total
                if pd.notna(patient_date_total)
                else None
            ),
            "calculated_mode_sum_matches_recorded_mode_sum": (
                mode_sum_calculated == patient_date_mode_sum_recorded
                if pd.notna(patient_date_mode_sum_recorded)
                else None
            ),

            "overall_gp_pf_patient_date_total": overall_total,
            "overall_gp_pf_patient_date_mode_sum": overall_mode_sum,
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
    "gp_pf_patient_date_f2f",
    "gp_pf_patient_date_online",
    "gp_pf_patient_date_telephone",
    "gp_pf_patient_date_othermode",
]

plot_df = df[df["measure"].isin(overall_mode_measures)].copy()
plot_df["mode"] = (plot_df["measure"].str.replace("gp_pf_patient_date_", "", regex=False))
plot_df["month"] = pd.to_datetime(plot_df["interval_start"]).dt.strftime("%Y-%m")
plot_pivot = plot_df.pivot(
    index="mode",
    columns="month",
    values="numerator",
)

ax = plot_pivot.plot(kind="bar",figsize=(8, 6),)
ax.set_ylabel("GP PF-related condition patient-date count")
ax.set_xlabel("Consultation mode")
ax.set_title("GP PF-related condition patient-date count by mode and month")

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("output/patient_measures_gp_pf_patient_date_by_mode_june.png",dpi=300,)
plt.close()