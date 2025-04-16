# MolQuery

Repository containing code and walkthrough for methods in the paper [*MolQuery: Prediction of lipid synthesizability using active learning*](paper_link).

MolQuery is a pipeline that integrates Active Learning (AL) to predict chemical synthesizability of lipid molecules designed for mRNA delivery via lipid nanoparticles (LNP). By leveraging AL, MolQuery efficiently trains machine learning models using limited datasets.

This repository includes an example simulating four rounds of AL to predict the transfection efficacy of lipid nanoparticles (LNP) using a public dataset from our previous work ([*Representations of lipid nanoparticles using large language models for transfection efficiency prediction*](https://academic.oup.com/bioinformatics/advance-article/doi/10.1093/bioinformatics/btae342/7684951)).

## Environment Setup
```
pip install -r requirements.txt
```

## Package Structure

- `data/`: contains sample data that can used to demonstrate the methods.
- `alien/`: contains source code for the selection framework with a CatBoost model. It contains wrappers for data, models, and classes to run candidate selection.
- `alien_selection.py`: main script that runs entropy-based candidate selection with a CatBoost model.
- `scripts/`: helper scripts that illustrate the MolQuery pipeline
- `protocol.sh`: bash script that simulates an annotator and runs through 4 rounds of Active Learning.