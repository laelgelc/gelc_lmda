# Artifact Naming Conventions (Slice v0)

All artifacts are written under output.artefacts_dir (default: artefacts/).

## Files
- artefacts/run.json
- artefacts/logs/run.log

- artefacts/vocabulary.csv
    - Columns: lemma, pos, rank, score, selection_method, k, seed, created_at

- Matrices:
    - artefacts/counts_raw.npz
    - artefacts/counts_norm.npz
    - artefacts/features.csv (lemma,pos,rank) — aligns with matrix columns

- Modeling:
    - artefacts/factors_loadings.csv   (K × N)
    - artefacts/factors_scores.csv     (docs × N)
    - artefacts/explained_variance.csv (length N)
    - artefacts/scree_plot.<png|svg>   (format from config.output.plot_format)

## Deterministic Ordering
- Vocabulary: sorted by rank ascending
- Features: sorted by rank ascending
- Scores and loadings: column order factor_1..factor_N; rows follow deterministic doc_id order

## Paths in run.json
- Paths are relative to the project root.
- Each artifact entry includes its SHA-256 to enable quick verification.