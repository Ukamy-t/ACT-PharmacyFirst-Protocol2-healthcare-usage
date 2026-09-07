import argparse
import gzip
import shutil


parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

with gzip.open(args.input, "rb") as input_file:
    with open(args.output, "wb") as output_file:
        shutil.copyfileobj(input_file, output_file)

print(f"Decompressed {args.input} to {args.output}")