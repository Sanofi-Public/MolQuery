"""Generate labelled and unlabelled pools for active learning."""

import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("data/iphos_multiclass.csv")
df = df.reset_index(drop=True)
df["lipid_id"] = df.index.astype(str)
df["SMILES"] = df["m1"]
df["label"] = df["y2"]

df_labelled, df_unlabelled = train_test_split(df, train_size=30, random_state=42)

df_unlabelled[["lipid_id", "SMILES"]].to_csv("data/unlabelled_pool.csv", index=False)
df_labelled[["lipid_id", "SMILES", "label"]].to_csv(
    "data/labelled_pool.csv", index=False
)
