import pandas as pd
import numpy as np
import os
import json

DATA_DIR = "data/"
FILE_NAME = "data.csv"
FINAL_DATA = "rearranged_data.xlsx"
DATA_SPECS = "data_specs.json"

with open(DATA_SPECS, 'r') as f:
    DATA_SPECS_DICT = json.load(f)

# Load data
df = pd.read_csv(os.path.join(DATA_DIR, FILE_NAME), delimiter=";")

# function to copy serial
def copy_serial(row):
    if not pd.isnull(row["ZG04"]):
        row["SERIAL"] = row["ZG04"]
    elif not pd.isnull(row["ZG05"]):
        row["SERIAL"] = row["ZG05"]
    return row

# move serial to serial from w01
df = df.apply(lambda row: copy_serial(row), axis=1)

# Drop lines where we have no serial number
df = df[~pd.isnull(df["SERIAL"])]

# Function to extract group
serial_group = dict()
def extract_variable(row):
    if not pd.isnull(row["ZG04"]):
        serial_group.update({row["SERIAL"]:"MS"})
    elif not pd.isnull(row["ZG05"]):
        serial_group.update({row["SERIAL"]:"AL"})

# Extract group
df.apply(lambda row: extract_variable(row), axis=1)

# Drop some unnecessary columns
df.drop(DATA_SPECS_DICT["drop_vars"], axis=1, inplace=True)

# Find all cases that have completed all the stuff
def collect_complete_cases():
    complete_cases = []
    for indiv in df["SERIAL"].unique():
        df_indiv = df[df["SERIAL"]== indiv]
        if df_indiv.shape[0] > 9:
            questionnaires = df_indiv["QUESTNNR"].values
            if ("MS_10" in questionnaires or "Altern10" in questionnaires) and "A2" in questionnaires and "wi01" in questionnaires:
                complete_cases.append(indiv)
    return complete_cases

complete_cases = collect_complete_cases()
df = df[df["SERIAL"].isin(complete_cases)]

value_vars_drop = ['SERIAL',"QUESTNNR"]
value_vars = [x for x in df.columns if x not in value_vars_drop]
df = pd.melt(df, id_vars=["SERIAL","QUESTNNR"], value_vars=value_vars)

# Drop variables without anser
df = df[~pd.isnull(df["value"])]

# Add group variable
df["GROUP"] = df["SERIAL"].apply(lambda val: serial_group[val])

# Rearrange table
df = df[["SERIAL", "GROUP", "QUESTNNR", "variable", "value"]]

# Store to new excel
df.to_excel(os.path.join(DATA_DIR, FINAL_DATA), index=False)
