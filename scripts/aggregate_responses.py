"""
A script to aggregate responses from the LNP labelling pipeline.
Input: excel file of responses and master csv file of synthesizeability data

script will match the image names to the index names in the selected.csv file to get the smiles for each response

output: master csv file of synthesizeability data with responses appended
"""

import argparse
import os
import sys
import numpy as np
import openpyxl
import pandas as pd


def convert_to_binary(response):
    """
    Convert an answer to a binary label (0/1).
    """
    # check if response is a string
    if isinstance(response, str):
        # check if response is yes
        if response.lower() in ("yes", "ys", "y"):
            return 1
        # check if response is no
        elif response.lower() in ("no", "n"):
            return 0
    return np.nan


def read_excel_with_openpyxl(file_path):
    """
    Process an excel file returning a formated dataframe.
    """
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    data = sheet.values
    # header is the first row of data
    cols = next(data)
    df = pd.DataFrame(data, columns=cols)

    # remove None values from the dataframe
    df = df.dropna(how="all")

    # if the dataframe has no rows, return None
    if df.shape[0] == 0:
        return None

    # get lipid id from file naming convention
    df["lipid_id"] = df["File Name"].apply(lambda x: int(x.split(".")[0]))
    # keep only the columns: lipid_id, Answer, Comments, Assigned To
    df = df[["lipid_id", "Answer", "Comments", "Assigned to"]]
    # convert answers to 0/1/none
    df["Answer"] = df["Answer"].apply(convert_to_binary)
    return df


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--responses", type=str)
    p.add_argument(
        "--unlabelled_pool",
        type=str,
        help="path to unlabelled pool of compounds",
    )
    p.add_argument(
        "--labelled_pool",
        type=str,
        help="path to labelled pool of compounds",
    )
    p.add_argument(
        "--output",
        type=str,
        help="path to output file",
    )
    p.add_argument(
        "--label_column",
        type=str,
        help="name of the column containing labels",
        default="synthesizable",
    )
    args = p.parse_args()

    # read in the excel file into a pandas dataframe
    responses = read_excel_with_openpyxl(args.responses)
    # rename the columns
    responses.columns = ["lipid_id", args.label_column, "comments", "assigned_to"]
    # remove rows without labels
    responses = responses.dropna(subset=[args.label_column])
    # no comments are acceptable, save them as empty strings instead of nans
    responses.comments = responses.comments.fillna("")
    # treat multiple annotations for a single compound
    responses = responses.groupby("lipid_id").agg(list)
    responses[args.label_column] = responses[args.label_column].apply(lambda x: x[0])
    responses.comments = responses.comments.apply("\n".join).apply(str.strip)

    print(responses)

    # read the unlabelled pool and match the smiles with lipid id
    df_pool = pd.read_csv(args.unlabelled_pool)[["lipid_id", "SMILES"]]
    responses = responses.merge(df_pool, on="lipid_id", how="left")

    # append the new rows to the current database
    df_labelled = pd.read_csv(args.labelled_pool)
    df_updated = pd.concat(
        [df_labelled, responses[["lipid_id", "SMILES", args.label_column, "comments"]]],
        ignore_index=True,
    )

    df_updated.to_csv(args.output, index=False)
    print(f"Size of the updated labelled pool: {df_labelled.shape}->{df_updated.shape}")


if __name__ == "__main__":
    main()
