import pandas as pd

"""
This script processes the patient-level SNOMED code count datasets generated for each PF condition.

For each PF condition:
- read the patient-level dataset;
- reshape the data from wide to long format;
- aggregate consultation counts to SNOMED-code level;
- merge with the corresponding SNOMED term lookup from the original codelist CSV;
- produce summary tables of the number of unique GP consultations in which each SNOMED code appeared;
- generates visualisations showing the most frequently recorded SNOMED codes for each PF condition.
"""

conditions = [
    "uti",
    "sinusitis",
    "insectbite",
    "otitismedia",
    "sorethroat",
    "shingles",
    "impetigo",
]

gp_snomed_codelist_files = {
    "uti": "codelists/pharmacy-first-project-urinary-tract-infection-and-related-conditions-for-pharamcy-first-clone.csv",
    "sinusitis": "codelists/pharmacy-first-project-sinusitis-related-conditions-administration-codes-for-pharmacy-first.csv",
    "insectbite": "codelists/pharmacy-first-project-insect-bites-and-related-conditions-administration-codes-for-pharmacy-first.csv",
    "otitismedia": "codelists/pharmacy-first-project-otitis-media-and-related-conditions.csv",
    "sorethroat": "codelists/pharmacy-first-project-Sore-throat-and-related-conditions.csv",
    "shingles": "codelists/pharmacy-first-project-shingles-and-related-conditions-for-pharmacy-first.csv",
    "impetigo": "codelists/pharmacy-first-project-impetigo-related-conditions-administration-codes-for-pharmacy-first.csv",
}

# all_summaries = []

for condition in conditions:
    print("Starting for condition:", condition, "...", flush=True)

    input_file = f"output/dataset_patients_snomed_{condition}.csv.gz"

    header = pd.read_csv(input_file, nrows=0)
    count_cols = [
        col for col in header.columns
        if col.startswith("count_")
    ]
    print(f"{condition}: {len(count_cols)} count columns", flush=True)

    # -------------------------------------------------
    # Sum count columns in chunks
    # -------------------------------------------------
    total_counts = pd.Series(0, index=count_cols, dtype="int64")

    for chunk in pd.read_csv(
        input_file,
        usecols=count_cols,
        chunksize=100_000,
        dtype={col: "int64" for col in count_cols},
        # low_memory=False,
    ):
        total_counts = total_counts.add(chunk.sum(), fill_value=0).astype("int64")

    summary = total_counts.reset_index()
    summary.columns = ["snomed_code", "consultation_count"]

    summary["snomed_code"] = (
        summary["snomed_code"]
        .str.replace("count_", "", regex=False)
        .astype(str)
    )

    # # Read patient-level SNOMED count dataset
    # df = pd.read_csv(input_file)

    # Read condition-specific codelist lookup
    lookup = pd.read_csv(gp_snomed_codelist_files[condition],dtype={"code": str},)
    lookup = lookup.rename(columns={"code": "snomed_code"})

    # Keep only relevant lookup columns
    if "term" in lookup.columns:
        lookup = lookup[["snomed_code", "term"]].drop_duplicates()
    else:
        lookup["term"] = ""
        lookup = lookup[["snomed_code", "term"]].drop_duplicates()
    
    summary = summary.merge(
        lookup,
        on="snomed_code",
        how="left",
    )
    
    # summary = (df[count_cols].sum().reset_index())

    # summary["snomed_code"] = (
    #     summary["snomed_code"]
    #     .str.replace("count_", "", regex=False)
    #     .astype(str)
    # )

    # # Add SNOMED term
    # summary = summary.merge(
    #     lookup,
    #     on="snomed_code",
    #     how="left",
    # )

    # Add condition column
    summary.insert(0, "condition", condition)

    summary = summary[
        ["condition", "snomed_code", "term", "consultation_count"]
    ]

    summary = summary.sort_values(
        "consultation_count",
        ascending=False,
    )

    output_file = f"output/snomed_count_summary_{condition}.csv"
    summary.to_csv(output_file, index=False)
    print(f"Saved: {output_file}", flush=True)

    # all_summaries.append(summary)


# final_summary = pd.concat(
#     all_summaries,
#     ignore_index=True,
# )
# output_file = "output/snomed_count_summary.csv"
# final_summary.to_csv(output_file, index=False)
# print(f"Saved: {output_file}")

# -------------------------------------------------
# Create plots for each condition
# -------------------------------------------------
# import matplotlib.pyplot as plt


# fig, axes = plt.subplots(
#     nrows=7,
#     ncols=1,
#     figsize=(40, 50),
# )

# axes = axes.flatten()

# top_n = 10


# for i, condition in enumerate(conditions):

#     ax = axes[i]

#     condition_df = final_summary[
#         final_summary["condition"] == condition
#     ].copy()

#     plot_df = (
#         condition_df
#         .sort_values("consultation_count", ascending=False)
#         .head(top_n)
#     )

#     # use term if available, otherwise SNOMED code
#     plot_df["label"] = (
#         plot_df["snomed_code"].astype(str)
#         + "\n"
#         + plot_df["term"].fillna("")
#     )

#     bars = ax.barh(
#         plot_df["label"],
#         plot_df["consultation_count"],
#     )

#     # add count labels
#     for bar, count in zip(bars, plot_df["consultation_count"]):

#         ax.text(
#             bar.get_width(),                 # x position
#             bar.get_y() + bar.get_height()/2,  # y position
#             f"{int(count):,}",              # formatted count
#             va="center",
#             ha="left",
#             fontsize=15,
#         )

#     ax.invert_yaxis()

#     ax.set_title(condition)

#     ax.set_xlabel("Consultation count")

#     ax.set_ylabel("SNOMED code / term")


# # # Remove unused final subplot
# # fig.delaxes(axes[-1])

# plt.tight_layout()

# plot_file = "output/snomed_count_top10_all_conditions.png"

# plt.savefig(plot_file, dpi=300)

# plt.close()

# print(f"Saved plot: {plot_file}")