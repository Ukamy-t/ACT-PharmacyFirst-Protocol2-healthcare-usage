
import pandas as pd
import os
import matplotlib.pyplot as plt
measures_dir = "output/measures"

# Source of pregnant/not pregnant status:
df = pd.read_csv(f"{measures_dir}/pregnant_source_all_ages.csv")
df = df.loc[df["sex"]=="female"] # drop males here, we asses rates in males and by age separately
# Extract year from interval_start
df['year'] = pd.to_datetime(df['interval_start']).dt.year

# Pivot the data to have sources as columns and years as index
pivot_df = df.pivot(index='year',columns='source', values='denominator')
print(pivot_df.head())
pivot_df.to_csv(f"{measures_dir}/flag_source_summary_by_year.csv")

# Plot a single bar chart showing the percentage for each source per year
def plotting(df, title, ylabel, xlabel, legend, filename):
    df.plot(kind='bar', figsize=(10, 6))
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.legend(title=legend)
    plt.tight_layout()
    plt.savefig(f"{measures_dir}/{filename}")
    plt.close()

plotting(df=pivot_df, title='Percentage from Each Source per Year', ylabel='Percentage', xlabel='Year', legend='Source', filename="flag_source_summary_by_year.png")

#df = df.groupby(["interval_start", "source"])["denominator"].sum()



# Identify all CSV files starting with "ck" in output/measures directory

#ck_files = [f for f in os.listdir(measures_dir) if f.startswith("ck") and f.endswith(".csv")]

# list all the pregnancy checks and their descriptions in a dictionary, 
# with the key as the filename (without .csv) and value as a list of description and suffix for weeks column
ck_descriptions = {
    "ck_diff_edd_end_current": ["EDD vs current pregnancy end", "_3"],
    "ck_diff_edd_end_recent": ["EDD vs recent pregnancy end", "_2"],
    "ck_diff_preg_ends": ["current vs recent pregnancy end", "_1"],
    "ck_pregnancy_future": ["future pregnancy code after recent delivery", ""]
}

# Import them as dataframes and create summary tables and plots for each

for file in ck_descriptions.keys():
    desc = ck_descriptions.get(file, ["Unknown check", ""])[0]
    suffix = ck_descriptions.get(file, ["Unknown check", ""])[1]
    print(f"Processing {file}: {desc}")
    
    ck_df = pd.read_csv(os.path.join(measures_dir, f"{file}.csv"))
    ck_df["weeks"] = ck_df["weeks"+ suffix] 
    ck_df['year'] = pd.to_datetime(ck_df['interval_start']).dt.year
    
    pivot_ck_df = ck_df.pivot(index='weeks', columns='year', values='numerator')
    pivot_ck_df.to_csv(f"{measures_dir}/{file}_summary_by_year.csv")
    print(pivot_ck_df)
    plotting(df=pivot_ck_df, title=desc, ylabel='Count', xlabel='Weeks', legend='Year', filename=f"{file}_by_year.png")



