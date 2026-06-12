
import pandas as pd
import os
import matplotlib.pyplot as plt
measures_dir = "output/measures"

age_band_list = ["o65", "16_19", "u16"]

for age_str in age_band_list:
    # Source of pregnant/not pregnant status:
    df = pd.read_csv(f"{measures_dir}/pregnant_source_{age_str}.csv")

    # Extract year from interval_start
    df['year'] = pd.to_datetime(df['interval_start']).dt.year

    # Pivot the data to have sources as columns and years as index
    pivot_df = df.loc[df["year"]==2026].pivot(index=['sex'], columns='source', values='numerator')
    pivot_df.to_csv(f"{measures_dir}/flag_source_{age_str}_summary_by_sex.csv")

    print(pivot_df)

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

    plotting(df=pivot_df, title='Count from Each Source by sex', ylabel='Count', xlabel='Sex', legend='Source', filename=f"flag_source_{age_str}_summary_by_sex.png")


# create function to rename the snomed column for linkage
def rename_code_column(df):
    code_col = df.columns[df.columns.str.lower().str.endswith("code")].tolist()
    df = df.rename(columns={code_col[0]: "code"})
    return df

# create function to link snomed descriptions
def link_codelists(file, codelist, ageband):
    input_file = f"output/measures/{file}_{age_str}.csv"
    # Read patient-level SNOMED count dataset
    df = pd.read_csv(input_file)
    df = rename_code_column(df)

    # Read condition-specific codelist lookup
    lookup = pd.read_csv(
        codelist,
        dtype={"code": int},
    )
    
    df = df.merge(
        lookup,
        on="code",
        how="left",
    )
    
    return df


#df = df.groupby(["interval_start", "source"])["denominator"].sum()


# list all the pregnancy checks and their descriptions in a dictionary, 
# with the key as the filename (without .csv) and codelist as the value, e.g. "pregnant_future_end_code": ["Future pregnancy end", "codelists/pharmacy-first-project-end-of-pregnancy-narrow.csv"]
file_descriptions = {
    "pregnant_future_end_code": ["Future pregnancy end", "codelists/pharmacy-first-project-end-of-pregnancy-narrow.csv"],
    "pregnant_recent_end_code": ["Recent pregnancy end", "codelists/pharmacy-first-project-end-of-pregnancy-narrow.csv"],
    "pregnant_pregnancy_code": ["Current pregnancy", "codelists/nhsd-primary-care-domain-refsets-preg_cod.csv"],
}

# Import them as dataframes and create summary tables and plots for each
for age_str in age_band_list:
    for file in file_descriptions.keys():
        # get string 
        desc = file_descriptions.get(file, ["Unknown check", ""])[0]
        
        codelist = file_descriptions.get(file, ["Unknown check", ""])[1]
        df = link_codelists(file, codelist, age_str)
        print(f"Processing {file}: {desc}")

        # Extract year from interval_start
        df['year'] = pd.to_datetime(df['interval_start']).dt.year

        # Pivot the data to have sources as columns and years as index
        pivot_df = df.loc[df["year"]==2026].groupby(["term","sex"])["numerator"].sum()#.reset_index().sort_values(by="numerator", ascending=False)
        pivot_df = pivot_df.unstack(level='sex')
        #pivot_df = df.loc[df["year"]==2026].pivot(index=['term'], columns='sex', values='numerator').sort_index()
        pivot_df.to_csv(f"{measures_dir}/summary_{age_str}_{file}.csv")

        print(pivot_df)


'''    
    
    pivot_ck_df = ck_df.pivot(index='weeks', columns='year', values='numerator')
    pivot_ck_df.to_csv(f"{measures_dir}/{file}_summary_by_year.csv")
    print(pivot_ck_df)
    plotting(df=pivot_ck_df, title=desc, ylabel='Count', xlabel='Weeks', legend='Year', filename=f"{file}_by_year.png")

'''

