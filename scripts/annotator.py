"""Script to simulate an annotator for the IPHOS dataset."""

import argparse

import pandas as pd

p = argparse.ArgumentParser()
p.add_argument("--input", type=str, default=None)
p.add_argument("--output", type=str, default="responses.xlsx")
p.add_argument("--database", type=str, default="data/iphos_multiclass.csv")
args = p.parse_args()

df = pd.read_csv(args.database)
df = df.reset_index(drop=True)
df["lipid_id"] = df.index
df["SMILES"] = df["m1"]
df["label"] = df["y2"]

# simulate an annotator
sel = pd.read_csv(args.input)
sel = sel.merge(df, on="lipid_id", how="left")
sel["Answer"] = sel.label.map({1: "Yes", 0: "No"})
sel["Comments"] = "This is an automated annotation, "
sel["Assigned to"] = "annotation@bot"
sel["File Name"] = sel["lipid_id"].apply(lambda x: f"{x}.png")
sel[["File Name", "Answer", "Comments", "Assigned to"]].to_excel(args.output)
