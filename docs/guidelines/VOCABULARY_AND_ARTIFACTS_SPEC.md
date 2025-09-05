# Vocabulary and Artifacts Specification (Slice v0)

## Vocabulary CSV
- Columns:
    - lemma (string)
    - pos (string or empty if not used)
    - rank (int, starting at 1)
    - score (float; selection score)
    - selection_method (enum: topk_loglik_v0)
    - k (int)
    - seed (int)
    - created_at (ISO 8601)
- Deterministic order = rank ascending.

## Document-Feature Matrix (DFM)
- Raw counts: counts_raw.(csv|npz) with shape (docs × K)
- Normalized per-thousand: counts_norm.(csv|npz)
- Feature list saved alongside (features.csv) with lemma,pos,rank.

## Modeling Outputs
- factors_loadings.csv: shape (K × N)
- factors_scores.csv: shape (docs × N)
- explained_variance.csv: length N
- scree_plot.(png|svg): elbow visualization

## run.json (Artifact Index)
- Includes:
    - config snapshot and dependency versions
    - paths and SHA-256 for each artifact
    - corpus stats, K, N, seed
    - timing per stage
