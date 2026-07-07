import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("output/dataset_practices.csv.gz")

df["interval_start"] = pd.to_datetime(df["interval_start"])
latest = df[df["interval_start"] == df["interval_start"].max()]

fig, axes = plt.subplots(3, 1, figsize=(10, 12))

# appointments boxplot
appt = latest["appointments_seen"].dropna()

axes[0].boxplot(appt, vert=False, showmeans=True)
axes[0].set_title("Practice-level distribution of GP appointments seen (boxplot)")
axes[0].set_xlabel("Appointments seen")

axes[0].text(appt.min(), 1.15, f"Min: {appt.min():.0f}")
axes[0].text(appt.max(), 1.15, f"Max: {appt.max():.0f}", ha="right")
axes[0].text(appt.mean(), 0.8, f"Mean: {appt.mean():.1f}", ha="center")
axes[0].text(appt.median(), 1.3, f"Median: {appt.median():.1f}", ha="center")

# population boxplot
pop = latest["population"].dropna()

axes[1].boxplot(pop, vert=False, showmeans=True)
axes[1].set_title("Practice-level distribution of population size (boxplot)")
axes[1].set_xlabel("Population")

axes[1].text(pop.min(), 1.15, f"Min: {pop.min():.0f}")
axes[1].text(pop.max(), 1.15, f"Max: {pop.max():.0f}", ha="right")
axes[1].text(pop.mean(), 0.8, f"Mean: {pop.mean():.1f}", ha="center")
axes[1].text(pop.median(), 1.3, f"Median: {pop.median():.1f}", ha="center")

# population histogram
axes[2].hist(pop, bins=50)

axes[2].set_title("Practice-level distribution of population size (histogram)")
axes[2].set_xlabel("Population size")
axes[2].set_ylabel("Number of practices")

# summary lines
axes[2].axvline(pop.mean())
axes[2].axvline(pop.median())

axes[2].text(pop.mean(), axes[2].get_ylim()[1]*0.8, f"Mean: {pop.mean():.0f}")
axes[2].text(pop.median(), axes[2].get_ylim()[1]*0.7, f"Median: {pop.median():.0f}")

# save
plt.tight_layout()
plt.savefig("output/practice_size_distribution.png", dpi=300, bbox_inches="tight")
plt.show()