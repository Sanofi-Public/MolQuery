"""
This is a simple script to aid the automation of our LNP synthesizeability labelling pipeline
It takes in a table (CSV) of LNP structures, selects a batch for labelling, generates images, names them and documents the selected in an output csv
"""

import argparse
import csv
import os

import pandas as pd
from rdkit import Chem
from rdkit.Chem import Draw


def draw_molecule(smiles_string, name):
    """
    number all carbon atoms and draw molecule
    """
    mol = Chem.MolFromSmiles(smiles_string)
    # Label carbon atoms
    for i, atom in enumerate(mol.GetAtoms()):
        if atom.GetAtomicNum() == 6:
            atom.SetAtomMapNum(i + 1)

    # Draw the molecule with atom labels
    img = Draw.MolToImage(
        mol, size=(900, 900), wedgeBonds=True, kekulize=True, wedgeInChiralBonds=True
    )
    img.save(name)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-i", "--input")
    p.add_argument("-d", "--dir")
    p.add_argument("-n", "--num_images", default=40)
    args = p.parse_args()

    # read in the unlabelled dataset and select samples for labelling
    df = pd.read_csv(args.input)

    selection = df.sample(int(args.num_images))
    leftover = df.drop(selection.index)

    # Output images and metadata
    os.makedirs(args.dir, exist_ok=True)
    selection.apply(
        lambda row: draw_molecule(row.SMILES, f"{args.dir}{row.lipid_id}.png"), axis=1
    )
    leftover.to_csv(f"{args.dir}leftover.csv", index=False)
    selection.to_csv(f"{args.dir}selected.csv", index=False)


if __name__ == "__main__":
    main()
