import argparse

import deepchem as dc
import pandas as pd
from sklearn.metrics import roc_auc_score

from alien.data import DeepChemDataset
from alien.models import CatBoostClassifier
from alien.selection import EntropySelector


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--labelled_dataset",
        type=str,
    )
    p.add_argument(
        "--unlabelled_dataset", type=str
    )
    p.add_argument("--output", type=str)
    p.add_argument("--model", type=str, default=None, help="model path")
    p.add_argument("--label_column", type=str, default="synthesizable")
    p.add_argument(
        "--batch_size", type=int, default=20, help="size of the batch to be selected"
    )
    p.add_argument("--seed", type=int, default=42, help="random seed")
    args = p.parse_args()

    # Load data
    df = pd.read_csv(args.labelled_dataset)
    smiles = df["SMILES"].values
    y = df[args.label_column].values
    print(y.shape)
    # Load in unlabelled data
    if args.unlabelled_dataset.endswith(".csv"):
        df_unlabelled = pd.read_csv(args.unlabelled_dataset)
    else:
        df_unlabelled = pd.read_csv(args.unlabelled_dataset, sep="\t")
    # Get rid of molecules already labeled
    unlabelled_smiles = df_unlabelled["SMILES"].values
    # Featurize data
    featurizer = dc.feat.CircularFingerprint(
        radius=3, size=2048, is_counts_based=True, chiral=True
    )
    loader = dc.data.InMemoryLoader(tasks=[args.label_column], featurizer=featurizer)
    dataset = loader.featurize(zip(smiles, y))

    # Split data
    splitter = dc.splits.RandomSplitter()
    train, test = splitter.train_test_split(dataset, seed=args.seed, frac_train=0.9)

    # Train CatBoost model
    if args.model is None:
        model = CatBoostClassifier(random_seed=args.seed, n_models=args.batch_size)
        model.fit(train.X, train.y)
        y_pred = model.predict_prob(test.X)
        roc = roc_auc_score(test.y, y_pred[:, 1])
        model.save("./model.cbm")
        print(f"ROC: {roc}")
    else:
        model = CatBoostClassifier()
        model.load(args.model)

    # Select new data to label with ALiEN
    data = DeepChemDataset(X=unlabelled_smiles, featurizer=featurizer)

    selector = EntropySelector(
        model=model,
        samples=data,
        batch_size=args.batch_size,
        precompute_entropy=False,
        n_starts=5,
    )
    batch = selector.select()
    ids = [r["ids"] for r in batch]
    df_sel = df_unlabelled.iloc[ids]
    df_sel.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
