import gzip
import shutil


INPUT_FILE = "output/dataset_patients_combined.csv.gz"
OUTPUT_FILE = "output/dataset_patients_combined.csv"


with gzip.open(INPUT_FILE, "rb") as input_file:
    with open(OUTPUT_FILE, "wb") as output_file:
        shutil.copyfileobj(input_file, output_file)

print(f"Decompressed {INPUT_FILE} to {OUTPUT_FILE}")