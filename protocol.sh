#!/bin/bash

# Prepare input data
python3 scripts/generate_pools.py

# Run 4 rounds of active learning
for round_id in 1 2 3 4;
do
    python3 alien_selection.py --labelled_dataset data/labelled_pool.csv --unlabelled_dataset data/unlabelled_pool.csv --output data/round_${round_id}.csv --label_column label
    python scripts/generate_images.py --input data/round_${round_id}.csv --dir data/round_${round_id}/ --num_images=20
    python scripts/annotator.py --input data/round_${round_id}/selected.csv  --output data/responses_${round_id}.xlsx
    python scripts/aggregate_responses.py --responses data/responses_${round_id}.xlsx --labelled_pool data/labelled_pool.csv --unlabelled_pool data/unlabelled_pool.csv --output data/labelled_pool.csv --label_column label
done