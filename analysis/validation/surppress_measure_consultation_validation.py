# https://docs.opensafely.org/outputs/sdc/

import pandas as pd
import matplotlib.pyplot as plt

input_file = "output/patient_measures_consultation_validation_summary.csv"
output_file = "output/patient_measures_consultation_validation_summary_release.csv"

summary_df = pd.read_csv(input_file)
release_df = summary_df.copy()

REDACTED = "[REDACTED]"

count_columns = [
    "pf_consultation",
    "pf_episode",
    "gp_consultation",
    "gp_episode",
    "ae_primary_count",
    "patient_has_non_primary_ae",
    "pf_consultation_eligibility_numerator",
    "pf_consultation_eligibility_denominator",
]


def round_to_nearest_5(x):
    return int(round(x / 5) * 5)


def suppress_count(x):
    if pd.isna(x):
        return x

    if x == 0:
        return 0

    if x <= 7:
        return REDACTED

    return round_to_nearest_5(x)


for col in count_columns:
    if col in release_df.columns:
        release_df[col] = release_df[col].apply(suppress_count)


# for idx, row in release_df.iterrows():
#     num = summary_df.loc[idx, "pf_consultation_eligibility_numerator"]
#     den = summary_df.loc[idx, "pf_consultation_eligibility_denominator"]

#     if pd.notna(num) and pd.notna(den) and (num <= 7 or den <= 7):
#         release_df.loc[idx, "pf_consultation_eligibility_ratio"] = REDACTED
#         release_df.loc[idx, "pf_consultation_eligibility_all_eligible"] = REDACTED

for idx, row in release_df.iterrows():
    raw_num = summary_df.loc[idx, "pf_consultation_eligibility_numerator"]
    raw_den = summary_df.loc[idx, "pf_consultation_eligibility_denominator"]

    release_num = release_df.loc[idx, "pf_consultation_eligibility_numerator"]
    release_den = release_df.loc[idx, "pf_consultation_eligibility_denominator"]

    if pd.notna(raw_num) and pd.notna(raw_den) and (raw_num <= 7 or raw_den <= 7):
        release_df.loc[idx, "pf_consultation_eligibility_ratio"] = REDACTED

        if "pf_consultation_eligibility_all_eligible" in release_df.columns:
            release_df.loc[idx, "pf_consultation_eligibility_all_eligible"] = REDACTED

    elif release_den in [0, REDACTED] or pd.isna(release_den):
        release_df.loc[idx, "pf_consultation_eligibility_ratio"] = None

        if "pf_consultation_eligibility_all_eligible" in release_df.columns:
            release_df.loc[idx, "pf_consultation_eligibility_all_eligible"] = None

    else:
        release_df.loc[idx, "pf_consultation_eligibility_ratio"] = (
            release_num / release_den
        )

        if "pf_consultation_eligibility_all_eligible" in release_df.columns:
            release_df.loc[idx, "pf_consultation_eligibility_all_eligible"] = (
                release_num == release_den
            )

release_df.to_csv(output_file, index=False)

########################################################
# PF consultation counts by condition (release version)
########################################################

plot_df = release_df[["month", "condition", "pf_consultation"]].copy()

plot_df["pf_consultation"] = pd.to_numeric(plot_df["pf_consultation"],errors="coerce",)

plot_pivot = plot_df.pivot(
    index="condition",
    columns="month",
    values="pf_consultation",
)

ax = plot_pivot.plot(kind="bar",figsize=(10, 6),)
ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.7,
)
ax.set_ylabel("PF consultation count")
ax.set_xlabel("Condition")
ax.set_title("PF consultation count by condition and month (disclosure control)")

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(
    "output/patient_measures_pf_consultations_by_condition_release.png",
    dpi=300,
)
plt.close()

########################################################
# GP consultation counts by condition (release version)
########################################################

plot_df = release_df[["month", "condition", "gp_consultation"]].copy()

plot_df["gp_consultation"] = pd.to_numeric(
    plot_df["gp_consultation"],
    errors="coerce",
)

plot_pivot = plot_df.pivot(
    index="condition",
    columns="month",
    values="gp_consultation",
)

ax = plot_pivot.plot(kind="bar",figsize=(10, 6),)
ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.7,
)
ax.set_ylabel("GP consultation count")
ax.set_xlabel("Condition")
ax.set_title("GP consultation count by condition and month (disclosure control)")

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(
    "output/patient_measures_gp_consultation_by_condition_release.png",
    dpi=300,
)
plt.close()