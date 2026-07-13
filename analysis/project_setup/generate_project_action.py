import yaml
import analysis.project_setup.config as config
from analysis.project_setup.config import month_range

# utilisation: python -m analysis/project_setup/generate_project_action.py > project_test.yaml

# start_dates = ["2024-02-01", "2024-03-01"]
start_dates = month_range(config.start, config.end)

project = {
    "version": "4.0",
    "actions": {
        "generate_dataset": {
            "run": "ehrql:v1 generate-dataset analysis/dataset_definition_patients.py --output output/dataset_patients.csv.gz",
            "outputs": {"highly_sensitive": {"dataset": "output/dataset_patients.csv.gz"}}
        }
    }
}

monthly_patient_actions = []

for d in start_dates:
    d_str = d.isoformat()
    action_name = f"generate_patient_dataset_{d_str.replace('-', '_')}"

    monthly_patient_actions.append(action_name)

    # This will generation a number of actions - each corresponds to generate one csv of a specified month
    project["actions"][action_name] = {
        "run": f"ehrql:v1 generate-dataset analysis/dataset_definition_patients.py --dummy-tables dummy_tables --output output/dataset_patients_{d_str}.csv.gz -- --start_date {d_str}",
        "outputs": {
            "highly_sensitive": {
                "dataset": f"output/dataset_patients_{d_str}.csv.gz"
            }
        }
    }

# This will generate one action that combines all monthly csvs
project["actions"]["combine_monthly_patient_gz"] = {
    "run": "python:v2 analysis/project_setup/preprocess_combine_gz.py --output output/dataset_patients_combined.csv.gz",
    "needs": monthly_patient_actions,
    "outputs": {
        "highly_sensitive": {
            "dataset": "output/dataset_patients_combined.csv.gz"
        }
    }
}

print(yaml.dump(project, sort_keys=False))