# CLI Guide (Slice v0)

## Commands
- lmda run --config config.yaml --input <corpus_dir> --output <artefacts_dir>
- Optional flags:
    - --seed <int>
    - --k <int> (Top-K vocabulary size)
    - --factors <int> (N factors)
    - --frozen-vocab <path> (reuse saved vocabulary)

## Exit Codes
- 0: success
- 1: invalid arguments/config
- 2: I/O or decoding errors
- 3: runtime errors (modeling, etc.)

## Outputs
- run.json (artifact index with hashes and metadata)
- vocabulary.csv
- counts_raw.(csv|npz), counts_norm.(csv|npz) per-thousand
- factors_loadings.csv, factors_scores.csv, explained_variance.csv
- scree_plot.(png|svg)
- logs/*.log

## Examples
- Minimal:
  lmda run --config config.yaml --input corpus/ --output artefacts/
- With frozen vocabulary:
  lmda run --config config.yaml --input corpus/ --output artefacts/ --frozen-vocab artefacts/vocabulary.csv

## Common Errors & Remedies
- Decoding error → check --encoding override or clean problematic files.
- Empty category → confirm subfolder contains readable .txt files.
- Too few documents for requested factors → reduce --factors or increase corpus size.